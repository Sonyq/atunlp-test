import socket
import thread
import json
import struct
import numpy as np
from cv2 import imwrite
from time import sleep


class Cliente():
    def __init__(self,host,port=9999):
        try:
            self.host_ip = host
            self.port = port
            self.sock = socket.socket()
            self.sock.connect((self.host_ip, self.port))
            self.conecxion = True
            self.flag_msj= False
            self.data = ""
            thread.start_new_thread(self.entrada,())
        except:
            print "la conexion al robot fallo IP: ",self.host_ip


    def entrada(self):
        while self.conecxion == True:
            try:
                byts = self.sock.recv(5)
                paquetes = self.sock.recv(int(byts))
                self.data = self.sock.recv(1024)   #aca cambia los numeritos pal bufer
                #for i in range(int(paquetes)):
                while len(self.data) != int(paquetes):
                    self.data+=self.sock.recv(1024)  #aca cambia los numeritos pal bufer (same shit)
                self.flag_msj = True
            except:
                print "Error en la recepcion de datos IP:",self.host_ip
                self.conecxion = False
            #self.data = self.recv_msg()
            #self.flag_msj = True

    def enviar(self,msj):
        try:
            self.sock.send(msj)
        except:
            print "Imposible enviar el msj IP:",self.host_ip


    def msjRobot(self):
        self.flag_msj = False
        return self.data

class Robot():
    def __init__(self,host,port=9999):
        self.clt = Cliente(host,port)

    def frenar(self):
        self.clt.enviar("frenar")

    def motor0(self,vel,t=-1): #velocidad,direccion(0 retroceder, 1 avanzar), tiempo (-1 indefinido)
        if abs(vel)<100 and abs(vel)>=0:
            self.clt.enviar("motor0") #comando del motor
            self.clt.enviar(json.dumps([vel,t if t >=0 else -1]))
        #[velocidad,tiempo]
            if t != -1:
                sleep(t if t >0 else 0)
                self.motor0(0,-1)

    def motor1(self,vel,t=-1):
        if abs(vel)<100 and abs(vel)>=0:
            self.clt.enviar("motor1") #comando del motor
            self.clt.enviar(json.dumps([vel,t if t >=0 else -1]))
            if t != -1:
                sleep(t if t>0 else 0)
                self.motor1(0,-1)
        #[velocidad,tiempo]

    def motores(self,vel1,vel2,t=-1):
        if abs(vel1)<= 100 and abs(vel1)>=0:
            if abs(vel2) <= 100 and abs(vel2)>=0:
                self.clt.enviar("motores")
                self.clt.enviar(json.dumps([vel1,vel2,t if t>=0 else -1]))
                if t != -1:
                    sleep(t if t>0 else 0)
                    self.motores(0,0,-1)
    def detener(self):
        self.motores(0,0,-1)

    def avanzar(self,vel,t=-1):
        self.motores(vel,vel,t)

    def retroceder(self,vel,t=-1):
        self.motores(-vel,-vel,t)

    def girarD(self,vel,t=-1):
        self.motores(vel,-vel,t)

    def girarI(self,vel,t=-1):
        self.motores(-vel,vel,t)

    def tomar_foto(self):
        self.clt.enviar("tomar_foto")

    def guardar_foto(self,dir):
        self.clt.enviar("guardar_foto")
        while self.clt.flag_msj != True:
            sleep(0.1)
        self.clt.flag_msj = False
        print self.clt.data,"-----",len(self.clt.data)
        imwrite(dir,np.fromstring(self.clt.data,dtype=np.uint8).reshape(480,640,3))

    def liberar_cam(self):
        self.clt.enviar("liberar_cam")








