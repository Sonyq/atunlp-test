#import RPi.GPIO as GPIO
from cv2 import VideoCapture,imwrite
from time import sleep

class Camara():
    def __init__(self):
        self.cam = VideoCapture(0)
        self.foto = ""

    def capturar(self):
        for i in range(10):
            self.cam.grab()
        self.foto = self.cam.read()[1]

    def guardar_foto(self,dir="img.png"):
        imwrite(dir,self.foto)
        
    def liberar_camara(self):
        self.cam.release()

class Robot():
    def __init__(self,compat):
     #   self.seteo_inicial()
     #   self.pwm_m0=GPIO.PWM(23,10000)
     #   self.pwm_m1=GPIO.PWM(24,10000)

     #   self.pwm_m0.start(0)
     #   self.pwm_m1.start(0)
        self.dic_comandos={"frenar":self.frenar,"motor0":self.motor0,"motor1":self.motor1,"motores":self.motores,"detener":self.detener,
                           "avanzar":self.avanzar,"retroceder":self.retroceder,"girarD":self.girarD,"girarI":self.girarI,
                           "tomar_foto":self.tomar_foto,"liberar_cam":self.liberar_cam}
        self.cam = Camara()
    def seteo_inicial(self):
        GPIO.setmode(GPIO.BCM)
        
        GPIO.setup(5,GPIO.IN)
        GPIO.setup(6,GPIO.IN)
        GPIO.setup(14,GPIO.IN)
        GPIO.setup(15,GPIO.IN)

        GPIO.setup(27,GPIO.OUT)#cooler
	
        GPIO.setup(23,GPIO.OUT)#EN1
        GPIO.setup(24,GPIO.OUT)#EN2
        GPIO.setup(12,GPIO.OUT)
        GPIO.setup(16,GPIO.OUT)
        GPIO.setup(20,GPIO.OUT)
        GPIO.setup(21,GPIO.OUT)
	
    def frenar(self):
        GPIO.output([12,16,20,21],False)

    def motor0(self,vel,t=-1): #velocidad,direccion(0 retroceder, 1 avanzar), tiempo (-1 indefinido)
        if vel>=0:
            GPIO.output(12,True)
            GPIO.output(20,False)
        else:
            GPIO.output(12,False)
            GPIO.output(20,True)
        self.pwm_m0.ChangeDutyCycle(abs(vel))
        
        if t != -1:
            sleep(t if t >0 else 0)
            self.motor0(0,-1)

    def motor1(self,vel,t=-1):
        if vel>=0:
            GPIO.output(16,True)
            GPIO.output(21,False)
        else:
            GPIO.output(16,False)
            GPIO.output(21,True)
        self.pwm_m1.ChangeDutyCycle(abs(vel))
        
        if t != -1:
            sleep(t if t >0 else 0)
            self.motor1(0,-1)

    def motores(self,vel1,vel2,t=-1):
        if vel1>=0:
            GPIO.output(12,True)
            GPIO.output(20,False)
        else:
            GPIO.output(12,False)
            GPIO.output(20,True)
            
        if vel2>=0:
            GPIO.output(16,True)
            GPIO.output(21,False)
        else:
            GPIO.output(16,False)
            GPIO.output(21,True)
            
        self.pwm_m0.ChangeDutyCycle(abs(vel1))
        self.pwm_m1.ChangeDutyCycle(abs(vel2))
        
        if t != -1:
            sleep(t if t >0 else 0)
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
        self.cam.capturar()
        
    def guardar_foto(self,dir):
        self.cam.guardar_foto(dir)

    def liberar_cam(self):
        self.cam.liberar_camara()
        
    

    
