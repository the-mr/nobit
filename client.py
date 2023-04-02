from keyz import genKeys, encM, decM
import requests
from fake_useragent import UserAgent
import socketio
import time
import json

privK, pubK = genKeys()
headerz = { 'User-Agent': UserAgent().random }
storeOptions = {}
inviteCodes = {}
url = "http://127.0.0.1/"
socketsurl = "http://127.0.0.1/"
#url = "http://bbw.hopto.org/"
#socketsurl = "http://bbw.hopto.org/"
sio = socketio.Client()

#option to connect to tor proxy
def optionTor() :
    toroption = input("Would you like to use tor for all connections ? : ").upper()[0]

    if toroption == "Y" :
        storeOptions["TOR"] = True
        status = connTor("checkip")

        if status == False :
            #not conneccted try again
            print("not connected to tor")
            pass
        elif status == True :
            #connected proceed
            print("connected to tor")

    elif toroption == "N" :
        storeOptions["TOR"] = False
        session = requests.session()
        storeOptions["SESSION"] = session
    else :
        print("Not a valid option")


def connTor(context) :
    proxiez = {'http': 'socks5://127.0.0.1:9050', 'https': 'socks5://127.0.0.1:9050'}

    if context == "checkip" :
        realip = requests.get('https://ident.me', headers=headerz).text
        torip = requests.get('https://ident.me', proxies=proxiez, headers=headerz).text

        if context == "checkip" and realip == torip :
            return False
            #return "Tor is not connected!"
        elif context == "checkip" and realip != torip :
            session = requests.session()
            session.proxies.update(proxiez)
            storeOptions["SESSION"] = session

            return True
            #return "Tor is connected!"


#enter random username
def getUsername() :
    userN = input("Username : ")

    storeOptions["USERNAME"] = userN

def setUsername() :
    pass

def optionInv() :
    inviteOption = input("request or input invite code : ").upper()[0]

    if inviteOption == "R" :
        storeOptions["CHOICEINVITE"] = inviteOption

    elif inviteOption == "I" :
        storeOptions["CHOICEINVITE"] = inviteOption
    else :
        print("Not a valid option")


def serverReq() : 
    session = storeOptions["SESSION"]
    serverPubKey = session.get(url + "getPubKey", headers=headerz)
    if serverPubKey.status_code == 200 :
        serverPubKey = serverPubKey.text
        storeOptions["SERVERKEY"] = serverPubKey
        #print("Server Public Key : %s" % serverPubKey)
    else :
        pass


def getInviteCode() :
    invCode = input("Enter Invite Code : ")
    #regex to verify invite code
    return invCode



#choose between :
def choiceInv():

    #get inviteOption
    chInv = storeOptions["CHOICEINVITE"]
    #get sessionOption
    session = storeOptions["SESSION"]
    #get serverKey
    serverKey = storeOptions["SERVERKEY"]

    #request invite code
    if chInv == "R" :

        #enc pubk && send pubK to server && recieve enc invite code
        encPubK = encM(pubK, serverKey)

        data = {"epk":encPubK}

        encInviteCode = session.post(url +"getInviteCode", json=data, headers=headerz)
            
        #decrypt invite code using privK
        if encInviteCode.status_code == 200 :
            encInviteCode = encInviteCode.text
            decInviteCode = decM(encInviteCode, privK)
            print("Invite Code Recieved : %s" % decInviteCode)
            roomname = input("Set Room Name : ")
            inviteCodes[decInviteCode] = {"decInviteCode":decInviteCode, "roomName":roomname}

            data = json.dumps({"userName":storeOptions["USERNAME"], "inviteCode":inviteCodes[decInviteCode]["decInviteCode"], "roomName":inviteCodes[decInviteCode]["roomName"]})
            encData = encM(data, serverKey)

            wsConnect()

            sio.emit('getRoom', {'data':encData})


        else :
            pass

                    #INIT WEBSOCKETS
                    #wait for new connection

                        #approve pubkey

                            #encrypt messages back and forth


    #input invite code
    if chInv == "I" :
        inviteCode = getInviteCode()

        #send pubK to server && wait for init clients approval
        encPubK = encM(pubK, serverKey)
        encInviteCode = encM(inviteCode, serverKey)

        data = {"epk":encPubK, "eic":encInviteCode}

        encRecordedResponse = session.post(url + "inputInviteCode", json=data, headers=headerz)

        if encRecordedResponse.status_code == 200 :
            wsConnect()
            inviteCodes[inviteCode] = {"decInviteCode":inviteCode}
            
            data = json.dumps({"userName":storeOptions["USERNAME"], "inviteCode":inviteCodes[inviteCode]["decInviteCode"]})
            encData = encM(data, serverKey)

            sio.emit('joinRoom', {"data":encData})
                
        else : 
            pass


def wsConnect() :
    sio.connect(socketsurl, wait_timeout=2)

def wsReq() :
    pass

def wsChat() :
    message = input("Send data to room : ")
    encM(message, needJeyger)


@sio.event
def connect() :
    print("\nConnected to Server\n")

@sio.on('joined')
def getNotNewUser(data) :

    encData = data["data"]
    stringJson = decM(encData, privK)
    data = json.loads(stringJson)

    newUserJoined = data["newUser"]
    print(newUserJoined)

@sio.on('response')
def getMessageFromRoom(data) :
    encData = data['data']

    

@sio.on('left')
def getNotNewUser(data) :
    print(data['newUser'])


def main() :

    optionTor()
    serverReq()
    getUsername()
    optionInv()
    choiceInv()

    time.sleep(2)

    #chatChoice = True
    #while chatChoice == True :
    #    chatChoice = wsChat()

main()

#sio.wait()
sio.disconnect()
exit()