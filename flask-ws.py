from flask import Flask, request, session
from flask_socketio import SocketIO, send, emit, disconnect, join_room, leave_room
import json
from threading import Lock
import secrets
import string
from keyz import genKeys, encM, decM


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secrets'
async_mode = None
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()


privK, pubK = genKeys()


rooms = []
roomOrgs = {}
roomIds = {}


def genInviteCode() : 
    stringSource = string.ascii_letters + string.digits + string.punctuation + string.ascii_lowercase + string.ascii_uppercase
    invCodeChar = ""

    for i in range(40):
        invCodeChar += secrets.choice(stringSource)

    charInvCodeList = list(invCodeChar)
    secrets.SystemRandom().shuffle(charInvCodeList)
    inviteCode = ''.join(charInvCodeList)

    return inviteCode


@app.route("/", methods=["GET"])
def nothing() :
    return "nothing here"

@app.route("/getPubKey", methods=["GET"])
def giveServerKey():
    return pubK

@app.route("/getInviteCode", methods=["POST"])
def giveIviteCode() :

    encPubKey = request.json["epk"]
    pubKey = decM(encPubKey, privK)

    inviteCode = genInviteCode()

    lenOfRoomIds = str(0)
    roomIds[inviteCode+lenOfRoomIds] = {'pubKey':pubKey}

    encCode = encM(inviteCode, pubKey)

    return encCode

@app.route("/inputInviteCode", methods=["POST"])
def recieveInviteCode() :
    encPubKey = request.json["epk"]
    encInviteCode = request.json["eic"]

    pubKey = decM(encPubKey, privK)
    invCode = decM(encInviteCode, privK)

    lenOfRoomIds = str(len(roomIds))
    roomIds[invCode+lenOfRoomIds] = {'pubKey':pubKey}

    return ""


@socketio.on('getRoom')
def createRoom(data):

    encData = data['data']
    stringJson = decM(encData, privK)
    data = json.loads(stringJson)

    userSid = request.sid
    username = data["userName"]
    room = data["inviteCode"]
    roomname = data["roomName"]

    if room in rooms :
        pass
    else :
        roomOrgs[room] = {'role':'master', "userSid":userSid, "username":username, "room":room, "roomname":roomname}
        join_room(room)

        data = json.dumps({"newUser": username+" joined " +roomname+"!"})

        lenOfRoomIds = str(0)
        pubKeyOfMaster = roomIds[room+lenOfRoomIds]["pubKey"]
        encData = encM(data, pubKeyOfMaster)

        emit('joined', {"data":encData}, to=room)



@socketio.on('joinRoom')
def joinARoom(data):

    encData = data['data']
    stringJson = decM(encData, privK)
    data = json.loads(stringJson)

    userSid = request.sid
    username = data["userName"]
    room = data["inviteCode"]

    if room in rooms :
        pass
    else :
        join_room(room)

        data = json.dumps({"newUser": username+" joined " +roomOrgs[room]["roomname"]+"!"})

        lenOfRoomIds = str(1)
        pubKeyOfUser = roomIds[room+lenOfRoomIds]["pubKey"]
        encData = encM(data, pubKeyOfUser)

        emit('joined', {"data":encData}, to=room)



@socketio.on('replyToRoom')
def message(data):
    encData = data['data']
    encRoom = data['room']

    stringJson = decM(encRoom, privK)
    room = json.loads(stringJson)

    emit('response', {"data": encData}, to=room)



@socketio.on('disconnect')
def disconnects():
    try :
        userSid = request.sid
        username = roomOrgs[userSid]["newUser"]
        roomname = roomOrgs[userSid]["roomname"]
        room = roomOrgs[userSid]["room"]

        roomOrgs.pop(userSid)

        leave_room(room)

        data = json.dumps({"newUser": username+" left " +roomOrgs[room]["roomname"]+"!"})

        lenOfRoomIds = str(1)
        pubKeyOfUser = roomIds[room+lenOfRoomIds]["pubKey"]
        encData = encM(data, pubKeyOfUser)

        emit('left', {"data":encData}, to=room)


        #emit('left', {'newUser': username+' left ' +roomname+'!'}, to=room)
        print('Client Disconnected')
    except :
        print("Client Disconnected")



if __name__ == '__main__' :
    socketio.run(app, host="127.0.0.1", port="80")





#generate new key pair everyday ||  when specificly to server, must encrypt with public key

#no userids

#random invite codes generated

#payed users get dedicated invite codes

