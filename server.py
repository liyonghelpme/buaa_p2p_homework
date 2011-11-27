import socket
import json
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(('0.0.0.0', 8002))
files = {}#uid filelist
while True:
    data = server.recvfrom(512)#at most 
    print data
    #0 clear set new
    #1 append files
    fi = json.loads(data[0])
    uid = data[1][0]+':'+str(data[1][1])
    if fi[0] == 0:
        files[uid] = fi[1]
    else:
        if files[uid] == None:
            files[uid] = fi[1]
        else:
            files[uid] += fi[1]
    echo = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    echo.connect(data[1])
    echo.send(uid)
    echo.close()

