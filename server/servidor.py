import SocketServer
import socket
import thread
import os
import json
import struct
#import RPi.GPIO as GPIO
from time import sleep
from artunilpo import *

class Server():
    def __init__(self):
        self.lista_clt=[]
        self.socket=socket.socket()
        self.host=([l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0])
        self.socket.bind((self.host, 9994))
        thread.start_new_thread(self.conection,())
        self.robot = Robot(1)
        self.out_timer=["motor0","motor1","motores","detener","avanzar","retroceder","girarD","girarI"]
        self.no_var=["frenar","detener","tomar_foto","liberar_cam"]
        self.dic_sv_comandos = {}

    def limpiar(self):
        os.system('clear')

    def conection(self,):
        while True:
            try:
                self.socket.listen(5)
                socket_cliente,datos_cliente=self.socket.accept()
                print "\nNuevo cliente se a conectado:",datos_cliente
                self.lista_clt.append(socket_cliente)
                self.avisodeconecxion(datos_cliente,True)
                thread.start_new_thread(self.entrada,(socket_cliente,datos_cliente))
            except:
                print "err"
                break


    def avisodeconecxion(self,datos_cliente,estado):
        if estado==True:
            aviso="Nuevo cliente se a conectado:"+str(datos_cliente)
        elif estado==False:
            aviso="Un cliente se a desconectado: "+str(datos_cliente)
            print aviso
	#for sockets in lista:
	#	sockets.send(aviso)
        return


    def entrada(self,socket_cliente,datos_cliente):
        msj=""
        while msj!= "salir":
 #           try:
                msj = socket_cliente.recv(40)
                if msj == "salir":
                    self.lista_clt.remove(socket_cliente)
                    self.avisodeconecxion(datos_cliente,False)
                    break
                elif msj == "guardar_foto":
                    self.enviar_foto(socket_cliente,self.robot.cam.foto)
                elif msj in self.no_var:
                    self.robot.dic_comandos[msj]()
                elif msj in self.robot.dic_comandos.keys():
                    variables=json.loads( socket_cliente.recv(25))
                    if msj in self.out_timer:
                        variables[-1]= -1
                        print variables
                        self.robot.dic_comandos[msj](*variables)
                        
            #except:
            #    print "El cliente D/C o tubo un error(entradasv)"
#		self.lista_clt.remove(socket_cliente)
#		self.avisodeconecxion(datos_cliente,False)
#		msj="salir"
#		GPIO.cleanup()
#		break
    def enviar_foto(self,socket_cliente,foto):
        data=foto.tostring()
        paquete,l_paquete=len(data),1024
        lista_msj=[data[i:i+l_paquete]for i in range(0,paquete,l_paquete)]
        #socket_cliente.send(str(len(str(len(lista_msj)))))
        #socket_cliente.send(str(len(lista_msj)))
        socket_cliente.send(str(len(str(len(data)))))
        socket_cliente.send(str(len(data)))
        
        for msj in lista_msj:
            socket_cliente.send(msj)
        #self.send_msg(socket_cliente,data)
        #print data,"-------",len(data),":",len(lista_msj)

def main():
        try:
            server=Server()
            SvEstatus=True
            print "\t\t","arturo"
            print "IP:",server.host
            while SvEstatus!=False:
                    comando=raw_input()

        finally:
                GPIO.cleanup()

main()
