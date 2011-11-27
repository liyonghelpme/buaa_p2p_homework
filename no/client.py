import socket
import json
import thread
import time
import struct

myIpPort = ()
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
files = []
print "input yout port:"
while True:
    try:
        myport = int(raw_input())
        client.bind(('0.0.0.0', myport))
        break
    except:
        print "port occupy retry"
print "input your files to share diliminate by empty:"
fi = raw_input()
fi = fi.split(' ')
for f in fi:
    print f
    with open(f, 'rb') as myf:
        files.append(f)

print fi
print "input server to connect IP port:"
ser = raw_input()
ser = ser.split(' ')
send = [0, files]
con = (ser[0], int(ser[1]))
#client.connect(con)

shutDown = False

state = 0#not connect 

def transferFile(fname, ipport):
    fserver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #fserver.connect(ipport)
    data = None
    with open(fname, 'rb') as f:
        data = f.read()
    if data == None:
        return
    f.close()
    print data
    #sendData:1  fid:  510file
    #response:0 error  1: no
    fid = 0
    no = 0
    while not shutDown:
        pack = struct.pack('B', 1)
        pack += struct.pack('B', no)
        
        if fid*510 < len(data):
            pack += data[fid*510:(fid+1)*510]
        else:#finish
            print "finish transfer"
            return
        print "file:", pack

        fserver.sendto(pack, ipport)
        fclient = fserver.recvfrom(512)
        res = fclient[0]
        opcode, = struct.unpack('B', res[0])
        if opcode == 0:#error retry
            continue

        resId, = struct.unpack('B', res[1])
        if opcode == 3 and resId == no:#check fno right
            fid += 1
            no = fid % (1 << 8)
        #error retry

def fetchIPPort():
    global client
    global send
    global con
    while not shutDown:
        client.sendto(json.dumps(send), con)
        ipport = client.recvfrom(512)#connect to fetch Data 
        print ipport
        global state
        if state == 0:#join server 
            state = 1
            break
        time.sleep(20)

    while not shutDown:
        ipport = client.recvfrom(512)#wait for send file request
        print ipport
        data = ipport[0]
        #byte  opcode 0 error 1 sendData 2 request for file 3:response
        #byte  after filename
        opcode, = struct.unpack('B', data[0])
        print "transfer file"
        print opcode
        if opcode == 2:
            fname = data[1:]
            thread.start_new_thread(transferFile, (fname, ipport[1]))

#fetch Ip:port listen to send file
thread.start_new_thread(fetchIPPort, ())


#fetchFile client
print "input host to fetch file ip,port:"
tar = raw_input()
tar = tar.split(' ')
fetchSer = (tar[0], int(tar[1]))
fetchClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#fetchClient.connect(fetchSer)


print "input file to fetch:"
fi = raw_input()
#2 request for file
opcode = struct.pack('B', 2)
opcode += fi
fetchClient.sendto(opcode, fetchSer)
tempfile = ''
sendFinish = False
while not sendFinish:
    res = fetchClient.recvfrom(512)
    print res
    opcode, = struct.unpack('B', res[0][0])
    if opcode == 1:#send data
        fid, = struct.unpack('B', res[0][1])
        data =  res[0][2:]
        tempfile += data
        if len(data) < 510:
            fi = file(fi, 'wb')
            fi.write(tempfile)
            fi.close()
            sendFinish = True
        else:
            fetchClient.sendto(struct.pack('BB', 3, fid), res[1])
    


