#import RPi.GPIO as GPIO
import thread
from cv2 import VideoCapture,imwrite
from time import sleep,time
#from RPIO import PWM
import atexit

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

class Hcsr4():
    def __init__(self):
        self.flag_busy = False
        self.trig = 15
        self.echo = 14
        self.delay_recov = 0.08 #sec
        self.t_out = 27 #milisec

    def flag(self):
        sleep(self.delay_recov)
        self.flag_busy = False

    def distancia(self):
        aux = self.flag_busy
        while self.flag_busy:
            sleep(0.03)
        else:
            if aux == True:
                return distance #se estaba midiendo, cuando termine directamente se devuelve la ultima medicion
            
        self.flag_busy = True

        GPIO.output(self.trig,True)
        sleep(0.00001)
        GPIO.output(self.trig,False)

        #channel = GPIO.wait_for_edge(self.echo,GPIO.RISING,timeout=self.t_out)
        while not GPIO.input(self.echo):
            pulse_start = time()
        
        #if channel is None:
        #    thread.start_new_thread(self.flag,())
        #    return -1 #fuera de rango
            
        #channel = GPIO.wait_for_edge(self.echo,GPIO.FALLING,timeout=self.t_out)
        while GPIO.input(self.echo):
            pulse_end = time()

        #if channel is None:
        #    thread.start_new_thread(self.flag,())
        #    return -1 #fuera de rango     

        pulse_duration = pulse_end - pulse_start
        distance = round((pulse_duration * 17150),2)
        if distance < 400 and distance > 2:
            return distance
        else:
            return -1


class Robot():
    def __init__(self,compat):
        #self.seteo_inicial()
        #self.pwm_m0=GPIO.PWM(23,4500)
        #self.pwm_m1=GPIO.PWM(24,4500)
        #PWM.set_loglevel(PWM.LOG_LEVEL_ERRORS)
        self.dma_channel = 1
        #PWM.setup(3)
        #PWM.init_channel(self.dma_channel,3000)
        self.offset_value=14
        self.ciclos=50
        self.duracion=20
        
        #self.pwm_m0.start(0)
        #self.pwm_m1.start(0)
        self.dic_comandos={"frenar":self.frenar,"motor0":self.motor0,"motor1":self.motor1,"motores":self.motores,"detener":self.detener,
                           "avanzar":self.avanzar,"retroceder":self.retroceder,"girarD":self.girarD,"girarI":self.girarI,
                           "tomar_foto":self.tomar_foto,"distancia":self.distancia}
        self.cam = Camara()
        self.sensor_distancia = Hcsr4()
        
    def seteo_inicial(self):
        GPIO.setmode(GPIO.BCM)
        
        GPIO.setup(5,GPIO.IN)
        GPIO.setup(6,GPIO.IN)

        GPIO.setup(14,GPIO.IN) #Hcsr4
        GPIO.setup(15,GPIO.OUT)

        GPIO.setup(27,GPIO.OUT)#cooler

        GPIO.setup(23,GPIO.OUT)#EN1
        GPIO.setup(24,GPIO.OUT)#EN2

        GPIO.setup(12,GPIO.OUT) #MA
        GPIO.setup(16,GPIO.OUT)

        GPIO.setup(20,GPIO.OUT)#MB
        GPIO.setup(21,GPIO.OUT)
	
    def frenar(self):
        GPIO.output([12,16,20,21],False)

    def motor0(self,vel,t=-1): #velocidad,direccion(0 retroceder, 1 avanzar), tiempo (-1 indefinido)
        if vel>=0:
            GPIO.output(12,True)
            GPIO.output(16,False)
        else:
            GPIO.output(12,False)
            GPIO.output(16,True)
        #self.pwm_m0.ChangeDutyCycle(abs(vel))
        if vel != 0:
            velocidad = (abs(vel) // 10) + 10
            for i in range(0,self.ciclos):
                PWM.add_channel_pulse(self.dma_channel,23,(self.duracion * i),velocidad)
        else:
            PWM.clear_channel_gpio(self.dma_channel,23)

        
        if t != -1:
            sleep(t if t >0 else 0)
            self.motor0(0,-1)

    def motor1(self,vel,t=-1):
        if vel>=0:
            GPIO.output(20,True)
            GPIO.output(21,False)
        else:
            GPIO.output(20,False)
            GPIO.output(21,True)
        #self.pwm_m1.ChangeDutyCycle(abs(vel))
        if vel != 0:
            velocidad = (abs(vel) // 10) + 10
            for i in range(0,self.ciclos):
                PWM.add_channel_pulse(self.dma_channel,24,(self.duracion * i),velocidad)
        else:
            PWM.clear_channel_gpio(self.dma_channel,24)
        
        if t != -1:
            sleep(t if t >0 else 0)
            self.motor1(0,-1)

    def motores(self,vel1,vel2,t=-1):
        if vel1>=0:
            GPIO.output(12,True)
            GPIO.output(16,False)
        else:
            GPIO.output(12,False)
            GPIO.output(16,True)
            
        if vel2>=0:
            GPIO.output(20,True)
            GPIO.output(21,False)
        else:
            GPIO.output(20,False)
            GPIO.output(21,True)
            
        #self.pwm_m0.ChangeDutyCycle(abs(vel1))
        #self.pwm_m1.ChangeDutyCycle(abs(vel2))
        if vel1 != 0 and vel2 != 0:
            #porcentaje_vel1= round((abs(vel1) // 10)*0.1, 2)
            #porcentaje_vel2= round((abs(vel2) // 10)*0.1, 2)
            #velocidad1 = int((self.duracion * porcentaje_vel1)+int(self.offset_value*(1 - porcentaje_vel1)))
            #velocidad2 = int((self.duracion * porcentaje_vel2)+int(self.offset_value*(1 - porcentaje_vel2)))
            velocidad1 = (abs(vel1) // 10) + 10 #thx luci :)
            velocidad2 = (abs(vel2) // 10) + 10
            for i in range(0,self.ciclos):
                PWM.add_channel_pulse(self.dma_channel,23,(self.duracion * i),velocidad1)
                PWM.add_channel_pulse(self.dma_channel,24,(self.duracion * i),velocidad2)
        else:
            PWM.clear_channel_gpio(self.dma_channel,23)
            PWM.clear_channel_gpio(self.dma_channel,24)
        
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

    def distancia(self):
        dist=self.sensor_distancia.distancia()
        self.sensor_distancia.flag()
        return dist
    
def cleanup():
    pass
    #GPIO.cleanup()
    #PWM.cleanup()

atexit.register(cleanup)
