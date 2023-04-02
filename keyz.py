import rsa
import base64
import json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

keys = {}

def genKeys() :
    (pubKey, privKey) = rsa.newkeys(2048) #can only encode 256 bytes

    keys["PubKey"] = pubKey
    keys["PubKeyPEM"] = pubKey.save_pkcs1().decode()
    keys["PrivKey"] = privKey
    keys["PrivKeyPEM"] = privKey.save_pkcs1().decode()

    return keys["PrivKeyPEM"], keys["PubKeyPEM"]



def encM(decMessage, pubKey) : 

    pubKey = rsa.PublicKey.load_pkcs1(pubKey.encode())

    randAesKey = rsa.randnum.read_random_bits(256) #32 bytes
    randIV = rsa.randnum.read_random_bits(128) # 16 bytes
    aesCipher = Cipher(algorithms.AES256(randAesKey), modes.CBC(randIV))
    aesEncryptor = aesCipher.encryptor()

    result = []

    for n in range(0,len(decMessage),245):
        part = decMessage[n:n+245]
        result.append( rsa.encrypt(part.encode(), pubKey) )

    pemEncMessage = b''.join(result)

    pemEncAesKey = rsa.encrypt(randAesKey, pubKey)
    pemEncIv = rsa.encrypt(randIV, pubKey)


    result2 = []

    for n in range(0,len(pemEncMessage),245):
        part = pemEncMessage[n:n+245]
        result2.append(aesEncryptor.update(part))

    aesEncMessage = b''.join(result2)
    aesEncMessage += b"\n\n\n\n\n" +pemEncAesKey+ b"\n\n\n\n\n" +pemEncIv

    encodedMessage = base64.b64encode(aesEncMessage).decode()

    return encodedMessage



def decM(b64Message, privKey) :
    privKey = rsa.PrivateKey.load_pkcs1(privKey.encode())

    encMessage = base64.b64decode(b64Message)

    #parse encMessage :
    encMessageList = encMessage.split(b"\n\n\n\n\n")
    aesEncMessage = encMessageList[0]
    pemEncAesKey = encMessageList[1]
    pemEncIv = encMessageList[2]

    #get aes info :
    randAesKey = rsa.decrypt(pemEncAesKey, privKey)
    randIv = rsa.decrypt(pemEncIv, privKey)
    aesCipher = Cipher(algorithms.AES256(randAesKey), modes.CBC(randIv))
    aesDecryptor = aesCipher.decryptor()

    result = []

    for n in range(0,len(aesEncMessage),245):
        part = aesEncMessage[n:n+245]
        result.append(aesDecryptor.update(part))

    pemEncMessage = b''.join(result)

    result2 = []

    for n in range(0,len(pemEncMessage),256):
        part = pemEncMessage[n:n+256]
        result2.append(rsa.decrypt(part, privKey))

    byteMessage = b''.join(result2)
    decryptedMessage = byteMessage.decode()

    return decryptedMessage

