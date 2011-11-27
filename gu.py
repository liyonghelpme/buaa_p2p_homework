# -*- coding: utf-8 -*-
import sys, os
import thread
import socket
from Tkinter import *
from client import *
class MyWin(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.grid()
        self.master.title("haha")
        self.after(3000, self.onTimer)
        self.connect = False
        self.data = MyBt()
        self.data.caller = self
        self.createWidgets()
        self.updateFileList()
        self.updatePeers()
        self.updateDownloads()
        self.addEntry.insert(0, 'test.txt')
        self.port.insert(0, '8080')
        self.ip.insert(0, '127.0.0.1')
        self.serport.insert(0, '8002')
    def onTimer(self):
        self.after(3000, self.onTimer)
    def __onDestroy(self, event):
        pass
    def updateFileList(self):
        self.shareList.delete(0, END);
        for d in self.data.files:
            self.shareList.insert(END, d)
    def updatePeers(self):
        self.fileList.delete(0, END)
        for d in self.data.peers:
            self.fileList.insert(END, str(d))
    def updateDownloads(self):
        self.downList.delete(0, END)
        for d in self.data.downloads:
            self.downList.insert(END, d)
    def selToDownload(self):
        items = self.fileList.curselection()
        try:
            items = map(int, items)
        except:
            return
        #ip, port, fname
        print items
        req = self.data.peers[items[0]]
        print "download", req
        self.data.fetchFile(req[0], req[1], req[2])
        self.data.downloads.append(str(req))
        self.updateDownloads()
    
    def createWidgets(self):
        upFrame = Frame(self)
        bottomFrame = Frame(self)

        upFrame.grid(row=0, column=0)
        bottomFrame.grid(row=1, column = 0)

        fileFrame = Frame(upFrame)
        fileFrame.grid(row=0, column=0, sticky=N+S)
        downloadFrame = Frame(upFrame)
        downloadFrame.grid(row=0, column=1, sticky=N+S)
        myShareFrame = Frame(upFrame)
        myShareFrame.grid(row=0, column=2, sticky=N+S)
        
        searchFrame = Frame(bottomFrame)
        searchFrame.grid(row=0, column = 0, sticky=W)

        conf = Frame(bottomFrame)
        conf.grid(row=1)
        
        ser = Frame(bottomFrame)
        ser.grid(row=2)


        Label(fileFrame, text='可下载文件').grid()
        Label(downloadFrame, text='已下载文件').grid()
        Label(myShareFrame, text='我的共享').grid()

        fileListFrame = Frame(fileFrame)
        fileListFrame.grid(row=1, column=0)
        fileScroll = Scrollbar(fileListFrame, orient=VERTICAL)
        fileScroll.grid(row=0, column=1, sticky=N+S)
        self.fileList = Listbox(fileListFrame, width=30, height=15, yscrollcommand=fileScroll.set)
        self.fileList.grid(row=0, column=0, sticky=N+S)
        fileScroll["command"] = self.fileList.yview

        downloadListFrame = Frame(downloadFrame)
        downloadListFrame.grid(row=1, column=0)
        downScroll = Scrollbar(downloadListFrame, orient=VERTICAL)
        downScroll.grid(row=0, column = 1, sticky=N+S)
        self.downList = Listbox(downloadListFrame, height=15,width=30, yscrollcommand=downScroll.set)
        self.downList.grid(row=0, column=0, sticky=N+S)
        downScroll["command"] = self.downList.yview
        
        shareListFrame = Frame(myShareFrame)
        shareListFrame.grid(row=1, column=0)
        shareScroll = Scrollbar(shareListFrame, orient=VERTICAL)
        shareScroll.grid(row=0, column=1, sticky=N+S)
        self.shareList = Listbox(shareListFrame, height=15, width=30, yscrollcommand=shareScroll.set)
        self.shareList.grid(row=0, column=0, sticky=N+S)
        shareScroll['command'] = self.shareList.yview
        
        downloadBut = Button(searchFrame, text="download", command=self.selToDownload)
        downloadBut.grid(row=0, column=0)
        self.searchBut = Button(searchFrame, text="search", command=self.onSearch, state = NORMAL)
        self.searchBut.grid(row=0, column=2)
        self.searchEntry = Entry(searchFrame, width=25)
        self.searchEntry.grid(row=0, column=1)

        self.addEntry = Entry(searchFrame, width=25)
        self.addEntry.grid(row=0, column=5)
        addFileBut = Button(searchFrame, text="addFile", command=self.onAdd)
        addFileBut.grid(row=0, column=6, sticky=W+E)
        removeFile = Button(searchFrame, text="removeFile", command=self.onRemove)
        removeFile.grid(row=0, column=7, sticky=W+E)

        connect = Button(ser, text="connect", command=self.onConnect)
        connect.grid(row=0, column = 6)
        Label(conf, text="监听端口:").grid(row=0, column=0)
        self.port = Entry(conf, width=25)
        self.port.grid(row=0, column = 1)
        listenBut = Button(conf, text="setListen", command=self.setListen) 
        listenBut.grid(row=0, column=2)

        Label(ser, text="目录服务器IP:").grid(row=0, column=2)
        Label(ser, text="端口:").grid(row=0, column=4)
        self.ip = Entry(ser, width=25)
        self.ip.grid(row=0, column=3)
        self.serport = Entry(ser, width=25)
        self.serport.grid(row=0, column=5)
    def setListen(self):
        self.data.setListenPort(int(self.port.get()))
    def onRemove(self):
        f = self.shareList.curselection()
        try:
            f = map(int , f);
        except:
            pass
        print f
        self.shareList.delete(ANCHOR)
        self.data.files.pop(f[0])


    def onAdd(self):
        f = self.addEntry.get()
        self.data.setFiles([f])
        self.updateFileList()
    def onSearch(self):
        self.data.search()
    def conSuc(self):
        self.searchBut.state = NORMAL
    def onConnect(self):
        self.myIpPort = int(self.port.get())
        self.data.setConnectSer(self.ip.get(), int(self.serport.get()))
        self.data.connect()
        #self.searchBut.state = NORMAL
def main():
    app =  MyWin()
    app.mainloop()
main()
