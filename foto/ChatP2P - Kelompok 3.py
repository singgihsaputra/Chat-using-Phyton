from Tkinter import *
from ScrolledText import *
from ttk import *
from PIL import ImageTk, Image
import os, re
import Tkinter
import socket
import thread

class ChatClient(Frame):
  
  def __init__(self, root):
    Frame.__init__(self, root)
    self.root = root
    self.initUI()
    self.serverSoc = None
    self.serverStatus = 0
    self.buffsize = 1024
    self.allClients = {}
    self.counter = 0
  
  def initUI(self):
    self.root.title("Simple P2P Chat Client")
    ScreenSizeX = self.root.winfo_screenwidth()
    ScreenSizeY = self.root.winfo_screenheight()
    self.FrameSizeX  = 690
    self.FrameSizeY  = 690
    FramePosX   = (ScreenSizeX - self.FrameSizeX)/2
    FramePosY   = (ScreenSizeY - self.FrameSizeY)/2
    self.root.geometry("%sx%s+%s+%s" % (self.FrameSizeX,self.FrameSizeY,FramePosX,FramePosY))
    self.root.resizable(width=False, height=False)
    
    padX = 10
    padY = 10
    parentFrame = Frame(self.root)
    parentFrame.grid(padx=padX, pady=padY, stick=E+W+N+S)
    
    ipGroup = Frame(parentFrame)
    serverLabel = Label(ipGroup, text="Set: ")
    self.nameVar = StringVar()
    self.nameVar.set("Username")
    nameField = Entry(ipGroup, width=20, textvariable=self.nameVar)
    self.serverIPVar = StringVar()
    self.serverIPVar.set("127.0.0.1")
    serverIPField = Entry(ipGroup, width=15, textvariable=self.serverIPVar)
    self.serverPortVar = StringVar()
    self.serverPortVar.set("8090")
    serverPortField = Entry(ipGroup, width=5, textvariable=self.serverPortVar)
    serverSetButton = Button(ipGroup, text="Set", width=10, command=self.handleSetServer)
    addClientLabel = Label(ipGroup, text="Add friend: ")
    self.clientIPVar = StringVar()
    self.clientIPVar.set("127.0.0.1")
    clientIPField = Entry(ipGroup, width=15, textvariable=self.clientIPVar)
    self.clientPortVar = StringVar()
    self.clientPortVar.set("8090")
    clientPortField = Entry(ipGroup, width=5, textvariable=self.clientPortVar)
    clientSetButton = Button(ipGroup, text="Add", width=10, command=self.handleAddClient)
    serverLabel.grid(row=0, column=0)
    nameField.grid(row=0, column=1)
    serverIPField.grid(row=0, column=2)
    serverPortField.grid(row=0, column=3)
    serverSetButton.grid(row=0, column=4, padx=5)
    addClientLabel.grid(row=0, column=5)
    clientIPField.grid(row=0, column=6)
    clientPortField.grid(row=0, column=7)
    clientSetButton.grid(row=0, column=8, padx=5)
    path = 'C:/Python27/sister/ciyus.jpg'
    readChatGroup = Frame(parentFrame)
	
    self.img= ImageTk.PhotoImage(Image.open(path))
    self.panel = Label(readChatGroup, image = self.img )
    self.profil = ScrolledText(readChatGroup, bg="white", width=50, height=10, state=DISABLED)
    self.receivedChats = ScrolledText(readChatGroup, bg="white", width=55, height=20, state=DISABLED)
    self.friends = Listbox(readChatGroup, bg="white", width=30, height=20)
    self.panel.pack(padx=0, pady=5, )
    self.profil.pack(padx=5, pady=5, )
    self.receivedChats.pack(padx=0, pady=100, side=LEFT)
    self.friends.pack(padx=5, pady=100, side=LEFT)

    writeChatGroup = Frame(parentFrame)
    self.chatVar = StringVar()
    self.chatField = Entry(writeChatGroup, width=90, textvariable=self.chatVar)
    sendChatButton = Button(writeChatGroup, text="Kirim", width=15, command=self.handleSendChat)
    self.chatField.grid(row=0, column=0, sticky=W)
    sendChatButton.grid(row=0, column=1, padx=5)
    self.statusLabel = Label(parentFrame)
    bottomLabel = Label(parentFrame, text="Modified By CREVION - PTIIK")
    ipGroup.grid(row=0, column=0)
    readChatGroup.grid(row=1, column=0)
    writeChatGroup.grid(row=2, column=0, pady=10)
    self.statusLabel.grid(row=3, column=0)
    bottomLabel.grid(row=4, column=0, pady=10)
    self.profil.config(state=NORMAL)
    
    self.profil.insert("end","Profil :\n\n")
    self.profil.config(state=DISABLED)
  def handleSetServer(self):
    if self.serverSoc != None:
        self.serverSoc.close()
        self.serverSoc = None
        self.serverStatus = 0
    serveraddr = (self.serverIPVar.get().replace(' ',''), int(self.serverPortVar.get().replace(' ','')))
    try:
        self.serverSoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSoc.bind(serveraddr)
        self.serverSoc.listen(5)
        self.setStatus("Server listening on %s:%s" % serveraddr)
        thread.start_new_thread(self.listenClients,())
        self.serverStatus = 1
        self.name = self.nameVar.get().replace(' ','')
        if self.name == '':
            self.name = "%s:%s" % serveraddr
    except:
        self.setStatus("Error setting up server")
    
  def listenClients(self):
    while 1:
      clientsoc, clientaddr = self.serverSoc.accept()
      self.setStatus("Client connected from %s:%s" % clientaddr)
      self.addClient(clientsoc, clientaddr)
      self.profil.config(state=NORMAL)
      try:
        data = clientsoc.recv(self.buffsize)
        if not data:
            break
        self.profil.insert("end","%s\n\n" % data)
      except:
          break
      self.profil.config(state=DISABLED)
      x = open("profil.txt", "r")
      semua = x.read()
      clientsoc.send(self.serverIPVar.get()+"("+self.nameVar.get()+") Terhubung"+"\n"+semua)
      thread.start_new_thread(self.handleClientMessages, (clientsoc, clientaddr))
    self.serverSoc.close()
  
  def handleAddClient(self):
    if self.serverStatus == 0:
      self.setStatus("Set server address first")
      return
    clientaddr = (self.clientIPVar.get().replace(' ',''), int(self.clientPortVar.get().replace(' ','')))
    try:
        clientsoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientsoc.connect(clientaddr)
        self.setStatus("Connected to client on %s:%s" % clientaddr)
        self.addClient(clientsoc, clientaddr)
        x = open("profil.txt", "r")
        semua = x.read()
        clientsoc.send(self.serverIPVar.get()+"("+self.nameVar.get()+") Terhubung"+"\n"+semua)
        self.profil.config(state=NORMAL)
        data = clientsoc.recv(self.buffsize)
        self.profil.insert("end","%s\n\n" % data)
        self.profil.config(state=DISABLED)
        thread.start_new_thread(self.handleClientMessages, (clientsoc, clientaddr))
    except:
        self.setStatus("Error connecting to client")

  def handleClientMessages(self, clientsoc, clientaddr):
    while 1:
      try:
        data = clientsoc.recv(self.buffsize)
        if not data:
            break
        self.addChat("%s:%s" % clientaddr, data)
      except:
          break
    self.removeClient(clientsoc, clientaddr)
    clientsoc.close()
    self.setStatus("Client disconnected from %s:%s" % clientaddr)
  
  def handleSendChat(self):
    if self.serverStatus == 0:
      self.setStatus("Set server address first")
      return
    msg = self.nameVar.get()+" : "+self.chatVar.get().replace(' ',' ')
    if msg == '':
        return
    for client in self.allClients.keys():
      client.send(msg)
    msg = "(saya)"+self.nameVar.get()+" : "+self.chatVar.get().replace(' ',' ')
    self.addChat("halo",msg)
  def addChat(self, client, msg):
    self.receivedChats.config(state=NORMAL)
    self.receivedChats.insert("end",msg+"\n")
    self.receivedChats.config(state=DISABLED)
  
  def addClient(self, clientsoc, clientaddr):
    self.allClients[clientsoc]=self.counter
    self.counter += 1
    self.friends.insert(self.counter,"%s:%s" % clientaddr)
  
  def removeClient(self, clientsoc, clientaddr):
      print self.allClients
      self.friends.delete(self.allClients[clientsoc])
      del self.allClients[clientsoc]
      print self.allClients
  
  def setStatus(self, msg):
    self.statusLabel.config(text=msg)
    print msg
      
def main():  
  root = Tk()
  app = ChatClient(root)
  root.mainloop()  

if __name__ == '__main__':
  main()  