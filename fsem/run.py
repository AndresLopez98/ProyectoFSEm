import sys
import RPi.GPIO as GPIO #Se importa la librería RPi.GPIO
from flask import Flask, render_template, Response, request #Response  sirve para recibir las imágenes desde la cámara web
import cv2 #Para la cámara
from camera import Camera
from time import sleep

app = Flask(__name__)

###Para el streaming de video se inicializan las varaibles
class CamaraVideo(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)


    def __del__(self):
        self.video.release()

    def get_frame(self):
        success, image = self.video.read()
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()

 
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
FOCO1 = 29
FOCO2 = 31
servo = 26
#DEFINIR LEDS COMO SALIDAS.
GPIO.setup(FOCO1, GPIO.OUT)   
GPIO.setup(FOCO2, GPIO.OUT) 
GPIO.setup(servo, GPIO.OUT) 

pwm = GPIO.PWM(servo, 40) #canal PWM con frecuencia de 40 Hz
pwm.start(0) #Ciclo de trabajo inicializado en cero


#LEDS APAGADOS 
GPIO.output(FOCO1, GPIO.LOW)
GPIO.output(FOCO2, GPIO.LOW)

#CREACIÓN DEL MENÚ PRINCIPAL

@app.route("/")
def index():

#ESTADO ACTUAL DE LOS LEDS   
    EstadoFOCO1 = GPIO.input(FOCO1)
    EstadoFOCO2 = GPIO.input(FOCO2)
 
    edoFOCO = {
            'FOCO1'  : EstadoFOCO1,
            'FOCO2'  : EstadoFOCO2,
        }
    return render_template('index.html', **edoFOCO)

#Función apertura de puertas


@app.route('/index', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        edoPuerta = request.form['edoPuerta']
        pwm.ChangeDutyCycle(float(edoPuerta))
        print(edoPuerta)
        sleep(1)
        pwm(ChangeDutyCycle(0))
        return render_template('index.html')

    return render_template('index.html')

#Esta función sirve para saber el estatus de la barra deslizante en la consola
@app.route('/desliza', methods=['POST', 'GET'])
def slider():
    received_data = request.data
    print(received_data)
    return received_data


#Función para la cámara y ruta /menu_camara
def gen(camera):
    while True:
        frame = camera.get_frame() #Se leen los frames de la cámara web o USB.
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/menu_camara')
def menu_camara():
    return Response(gen(CamaraVideo()), #Generador Response de Fask
                    mimetype='multipart/x-mixed-replace; boundary=frame')
     
#Se reciben los parámetros dependiendo del botón presionado.
@app.route("/<dispositivo>/<modo>")

#Esta función sirve para encender o apagar el foco al presionar el botón.
def modo(dispositivo, modo):
    if dispositivo == 'FOCO1':
        presiona = FOCO1
    if dispositivo == 'FOCO2':
        presiona = FOCO2
    if modo == "encendido":
        GPIO.output(presiona, GPIO.HIGH)
    if modo == "apagado":
        GPIO.output(presiona, GPIO.LOW)
              
    EstadoFOCO1 = GPIO.input(FOCO1)
    EstadoFOCO2 = GPIO.input(FOCO2)




    edoFOCO = {
        'FOCO1'  : EstadoFOCO1,
        'FOCO2'  : EstadoFOCO2,

    }
    return render_template('index.html', **edoFOCO)
 
if __name__ == "__main__":
   app.run(host='10.0.0.9', port=5000, debug=True)