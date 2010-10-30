import threading
import socket
import struct
import hashlib
import re
g_Req = {}

def _hexify(s):
    return re.sub('.', lambda x: '%02x ' % ord(x.group(0)), s)

def start_server():
    tick = 0
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', 1234))
    sock.listen(100)
    while True:
        print 'listening...'
        csock, address = sock.accept()
        tick+=1
        print 'connection!' 
        handshake(csock, tick)
        print 'handshaken'
        #interact(csock,25)
        for x in range(20,50):
            interact(csock, x,x+10)
            #tick+=1


def parse_incoming_shake(raw_shake):
    l = raw_shake.split("\r\n")
    #print l
    for e in l:
        line = e.split(": ")
       # print line
        if len(line) >= 2:
            g_Req[line[0]] = line[1]
    #print g_Req 

def send_data(client, str):
    #_write(request, '\x00' + message.encode('utf-8') + '\xff')
    str = '\x00' + str.encode('utf-8') + '\xff'
    return client.send(str)
def recv_data(client, count):
    data = client.recv(count) 
    #print data[-8:]
    g_Req['rand']=data[-8:]
    print ("all data is \n %s" % _hexify(data))
    return data.decode('utf-8', 'ignore')
    #return data
def getKeyNumber(keystr):
    val = 0
    for s in keystr:
        if s >= '0' and s <= '9':
            val = val*10 + int(s)
    return val

def handshake(client, tick):
    our_handshake = "HTTP/1.1 101 Web Socket Protocol Handshake\r\n"
    our_handshake+="Upgrade: WebSocket\r\n"
    our_handshake+="Connection: Upgrade\r\n"
    our_handshake+="Sec-WebSocket-Origin: file://\r\n"
    our_handshake+="Sec-WebSocket-Location: ws://localhost:1234/websession\r\n"
    our_handshake+="\r\n"


    
    shake = recv_data(client, 255)
    parse_incoming_shake(shake)
    print shake
    #We want to send this without any encoding
    print"---- we respond:"
    key1 = getKeyNumber(g_Req['Sec-WebSocket-Key1'])
    key2 = getKeyNumber(g_Req['Sec-WebSocket-Key2'])
    sp1 = g_Req['Sec-WebSocket-Key1'].count(" ")
    sp2 = g_Req['Sec-WebSocket-Key2'].count(" ")
    
    if key1 % sp1 != 0 or key2 % sp2 != 0:
        print "error reading websocket key"
    p1 = key1/sp1
    p2 = key2/sp2
  
    #print g_Req

    p3 = g_Req['rand']
    print ("p3is %s" % _hexify(p3))

    challenge = ""
    challenge += struct.pack("!I",p1)
    challenge += struct.pack("!I",p2)
    challenge += p3
    print ("challenge %s" % _hexify(challenge))
    md5c = hashlib.md5(challenge).digest()
    print ("md5 %s" % _hexify(md5c))
    our_handshake+=md5c
    print our_handshake
    client.send(our_handshake)

def interact(client, x,y):
    #data = recv_data(client, 255)
    #print 'got:%s' %(data)
    send_data(client,"%d %d %d" % (1,x,y))
    #send_data(client, "clock ! tick%d" % (tick))
    #send_data(client, "out ! %s" %(data))

if __name__ == '__main__':
    start_server()
