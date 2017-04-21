import RPi.GPIO as GPIO
from cv2 import VideoCapture,imwrite
from time import sleep,time
from RPIO import PWM
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

class Bumper():
    def __init__(self):
        self.pin_list = [18,25]
    def valor(self,sensor):
        if sensor < len(self.pin_list):
            return 1 if GPIO.input(self.pin_list[sensor]) else 0
    def todos(self):
        l_values = []
        for pin in self.pin_list:   #leo la lista de pines de los BUMPERS y devuelvo sus valores de entrada.
            l_values.append(1 if GPIO.input(pin) else 0)
        return l_values
    

class Cny70():
    def __init__(self):
        self.pin_list = [5,6,13,19,26]

    def valor(self,sensor):
        if sensor < len(self.pin_list):
            return 1 if GPIO.input(self.pin_list[sensor]) else 0
    def todos(self):
        l_values = []
        for pin in self.pin_list:   #leo la lista de pines de los CNY70 y devuelvo sus valores de entrada.
            l_values.append(1 if GPIO.input(pin) else 0)
        return l_values

class Hcsr4():
    def __init__(self):
        self.flag_busy = False
        self.distance = -1
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
                return self.distance #se estaba midiendo, cuando termine directamente se devuelve la ultima medicion
            
        self.flag_busy = True

        GPIO.output(self.trig,True) #pulso de 10 uSeg en Trig para comenzar a medir
        sleep(0.00001)
        GPIO.output(self.trig,False)

        while not GPIO.input(self.echo): #espero la respuesta del sensor de que va a comenzar a medir
            pulse_start = time()

        while GPIO.input(self.echo):    #mido el tiempo en 1 del pulso del pin ECHO, para saber la distancia.
            pulse_end = time()

        #calculos necesario para saber la distancia en base al tiempo de onda:
        pulse_duration = pulse_end - pulse_start
        distance = round((pulse_duration * 17150),2)
        if distance < 400 and distance > 2: #si la distancia no supera los 400 especificados por el fabricante, se devuelve.
            self.distance = distance
            return distance
        else:                       #medicion fuera de rango
            self.distance = -1
            return -1


class Robot():
    def __init__(self,compat): #compat es por la ip en modo conectividad.
        self.seteo_inicial()
        #seteos del PWM:
        self.dma_channel = 1
        PWM.setup(3)
        PWM.init_channel(self.dma_channel,3000)
        self.offset_value=14
        self.ciclos=50
        self.duracion=20

        #agrego los comandos a un diccionario para utilizar en el servidor.py:
        self.dic_comandos={"frenar":self.frenar,"motor0":self.motor0,"motor1":self.motor1,"motores":self.motores,"detener":self.detener,
                           "avanzar":self.avanzar,"retroceder":self.retroceder,"girarD":self.girarD,"girarI":self.girarI,
                           "tomar_foto":self.tomar_foto,"distancia":self.distancia,"leerLinea":self.leerLinea, "paraGolpes":self.paraGolpes}
        self.cam = Camara()
        self.sensor_distancia = Hcsr4()
        self.sensor_cny70 = Cny70()
        self.sensor_bumper = Bumper()
    def seteo_inicial(self):
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(14,GPIO.IN) #Hcsr4
        GPIO.setup(15,GPIO.OUT)

        GPIO.setup(27,GPIO.OUT)#cooler

        GPIO.setup(23,GPIO.OUT)#EN1
        GPIO.setup(24,GPIO.OUT)#EN2

        GPIO.setup(12,GPIO.OUT) #MA
        GPIO.setup(16,GPIO.OUT)

        GPIO.setup(20,GPIO.OUT)#MB
        GPIO.setup(21,GPIO.OUT)

        GPIO.setup(5,GPIO.IN) #CNY70
        GPIO.setup(6,GPIO.IN)
        GPIO.setup(13,GPIO.IN)
        GPIO.setup(19,GPIO.IN)
        GPIO.setup(26,GPIO.IN)

        GPIO.setup(18,GPIO.IN)#BIGOTES(Bumpers)
        GPIO.setup(25,GPIO.IN)

	
    def frenar(self):
        GPIO.output([12,16,20,21],False) #todos los pines de direccion en 0, esta es otra forma de detener los motores.

    def motor0(self,vel,t=-1): #(velocidad, tiempo = -1 es indefinido)
        if vel>=0:                  #si velocidad mayor a 0, seteo las direcciones del motor (MA) en modo avanzar:
            GPIO.output(12,True)    #pin 12(MA1) en 1
            GPIO.output(16,False)   #pin 16(MA2) en 0
        else:                       #si velocidad menor a 0, seteo las direcciones del motor (MA) en modo retroceder:
            GPIO.output(12,False)   #pin 12(MA1) en 0
            GPIO.output(16,True)    #pin 16(MA2) en 1

        if vel != 0:                #velocidad != 0, se setea el PWM correspodiente a ese % de velocidad.
            velocidad = (abs(vel) // 10) + 10
            for i in range(0,self.ciclos):
                PWM.add_channel_pulse(self.dma_channel,23,(self.duracion * i),velocidad) #PWM en el EN1 del motor MA
        else:
            PWM.clear_channel_gpio(self.dma_channel,23) #EN1 en 0, el motor no puede moverse.

        if t != -1:                     #si el tiempo es distinto a -1 el motor avanza por tiempo un tiempo dado
            sleep(t if t >0 else 0)
            self.motor0(0,-1)           #luego se detiene

    def motor1(self,vel,t=-1):
        if vel>=0:                  #si velocidad mayor a 0, seteo las direcciones del motor (MB) en modo avanzar:
            GPIO.output(20,True)    #pin 20(MB1) en 1
            GPIO.output(21,False)   #pin 21(MB2) en 0
        else:                       #si velocidad menor a 0, seteo las direcciones del motor (MB) en modo retroceder:
            GPIO.output(20,False)   #pin 20(MB1) en 0
            GPIO.output(21,True)    #pin 21(MB2) en 1

        if vel != 0:
            velocidad = (abs(vel) // 10) + 10
            for i in range(0,self.ciclos):
                PWM.add_channel_pulse(self.dma_channel,24,(self.duracion * i),velocidad) #PWM en el EN2 del motor MB
        else:
            PWM.clear_channel_gpio(self.dma_channel,24)#EN2 en 0, el motor no puede moverse.
        
        if t != -1:
            sleep(t if t >0 else 0)
            self.motor1(0,-1)

    def motores(self,vel1,vel2,t=-1):   #lo mismo que los anteriores pero ambos motores al mismo tiempo.
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

        if vel1 != 0 and vel2 != 0:
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
    
    def leerLinea(self):
        return self.sensor_cny70.todos()
    
    def paraGolpes(self):
        return self.sensor_bumper.todos()
    
def cleanup():
    GPIO.cleanup()  #libero los pines que setie en el programa
    PWM.cleanup()   #elimino los PWM en pines EN1 y EN2

atexit.register(cleanup) #me aseguro q se ejecute clean up, sea cual sea la forma de salida de programa.
