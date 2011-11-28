import socket
import json
import thread
import time
import struct
class MyBt:
    def __init__(self):
        self.files = []
        self.peers = []
        self.downloads = []
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.shutDown = False
    def doSearch(self):
        directCli = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        directCli.sendto(json.dumps([2]), self.con)
        data = directCli.recvfrom(1024)
        print data
        data = json.loads(data[0])
        self.peers = []
        for key in data:
            ip = key.split(':')
            port = ip[1]
            ip = ip[0]
            for f in data[key]:
                self.peers.append([ip, port, f]) 
        print self.peers
        self.caller.updatePeers()
    def search(self):
        thread.start_new_thread(self.doSearch, ())
    def setFiles(self, files):
        for f in files:
            print f
            with open(f, 'rb') as myf:
                self.files.append(f)
    def setListenPort(self, port):
        print port
        self.myport = int(port)
        self.client.bind(('0.0.0.0', port))
    def setConnectSer(self, ip, port):
        self.con = (ip, int(port))
    def connect(self):
        thread.start_new_thread(self.fetchIPPort, ())
    def transferFile(self, fname, ipport):
        fserver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
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
        while not self.shutDown:
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

    def fetchIPPort(self):
        state = 0
        while not self.shutDown:
            self.client.sendto(json.dumps([0, self.files]), self.con)
            ipport = self.client.recvfrom(512)#connect to fetch Data 
            print ipport
            self.natip = ipport[0]
            if state == 0:#join server 
                state = 1
                break
            time.sleep(20)
        self.caller.conSuc()
        while not self.shutDown:
            ipport = self.client.recvfrom(512)#wait for send file request
            print ipport
            data = ipport[0]
            #byte  opcode 0 error 1 sendData 2 request for file 3:response
            #byte  after filename
            opcode, = struct.unpack('B', data[0])
            print "transfer file"
            print opcode
            if opcode == 2:
                fname = data[1:]
                thread.start_new_thread(self.transferFile, (fname, ipport[1]))
    
    def fetchFile(self, tarip, tarport, fname):
        thread.start_new_thread(self.doFetchFile, (tarip, tarport, fname))
    def doFetchFile(self, tarip, tarport, fname):
        fetchSer = (tarip, int(tarport))
        fetchClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        opcode = struct.pack('B', 2)        
        opcode += fname
        fetchClient.sendto(opcode, fetchSer)
        #start new thread run this
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
                    fi = file(fname+'_bt', 'wb')
                    fi.write(tempfile)
                    fi.close()
                    sendFinish = True
                else:
                    fetchClient.sendto(struct.pack('BB', 3, fid), res[1])
    


