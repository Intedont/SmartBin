from time import sleep
import RPi.GPIO as GPIO
import picamera
import numpy as np
import tflite_runtime.interpreter as tflite
import paho.mqtt.client as mqtt
from keras_preprocessing.image import load_img
from keras_preprocessing.image import img_to_array


GPIO.setwarnings(False)

GPIO.setmode(GPIO.BOARD)
#GPIO.cleanup()

in1 = 11
in2 = 13
in3 = 15
in4 = 16

buttonGPIO = 12

dropGPIO = 8

step_timeout = 0.0105
impulse_timeout = 0.008

resX = 3280
resY = 2464
boxSide = 1700

labelToAngle = {
    0: -150,
    1: 90,
    2: 165,
    3: -150,
    4: -90,
    5: 0
}

labelToString = {
    0: 'cardboard',
    1: 'glass',
    2: 'metal',
    3: 'paper',
    4: 'plastic',
    5: 'trash'
}

GPIO.setup(in1, GPIO.OUT)
GPIO.output(in1, GPIO.LOW)

GPIO.setup(in2, GPIO.OUT)
GPIO.output(in2, GPIO.LOW)

GPIO.setup(in3, GPIO.OUT)
GPIO.output(in3, GPIO.LOW)

GPIO.setup(in4, GPIO.OUT)
GPIO.output(in4, GPIO.LOW)

GPIO.setup(buttonGPIO, GPIO.IN, pull_up_down = GPIO.PUD_UP)

GPIO.setup(dropGPIO, GPIO.OUT)


def genBox(resX = 3280, resY = 2464, boxSide = 1400):
    leftTopX = (resX / 2) - ( boxSide / 2 )
    leftTopY = (resY / 2) - ( boxSide / 2 )
    rightBottomX = (resX / 2) + ( boxSide / 2 )
    rightBottomY = (resY / 2) + ( boxSide / 2 )
    print(leftTopX, leftTopY, rightBottomX, rightBottomY)
    return ((leftTopX, leftTopY, rightBottomX, rightBottomY))

def forward(steps):
    for i in range(steps):
            GPIO.output(in1, GPIO.HIGH)
            GPIO.output(in2, GPIO.HIGH)
            sleep(impulse_timeout)
            GPIO.output(in1, GPIO.LOW)
            GPIO.output(in2, GPIO.LOW)

            GPIO.output(in2, GPIO.HIGH)
            GPIO.output(in3, GPIO.HIGH)
            sleep(impulse_timeout)
            GPIO.output(in2, GPIO.LOW)
            GPIO.output(in3, GPIO.LOW)
            
            GPIO.output(in3, GPIO.HIGH)
            GPIO.output(in4, GPIO.HIGH)
            sleep(impulse_timeout)
            GPIO.output(in3, GPIO.LOW)
            GPIO.output(in4, GPIO.LOW)
            
            GPIO.output(in4, GPIO.HIGH)
            GPIO.output(in1, GPIO.HIGH)
            sleep(impulse_timeout)
            GPIO.output(in4, GPIO.LOW)
            GPIO.output(in1, GPIO.LOW)
            
def backward(steps):
    for i in range(steps):
            
            GPIO.output(in4, GPIO.HIGH)
            GPIO.output(in1, GPIO.HIGH)
            sleep(impulse_timeout)
            GPIO.output(in4, GPIO.LOW)
            GPIO.output(in1, GPIO.LOW)
            
            GPIO.output(in3, GPIO.HIGH)
            GPIO.output(in4, GPIO.HIGH)
            sleep(impulse_timeout)
            GPIO.output(in3, GPIO.LOW)
            GPIO.output(in4, GPIO.LOW)
            
            GPIO.output(in2, GPIO.HIGH)
            GPIO.output(in3, GPIO.HIGH)
            sleep(impulse_timeout)
            GPIO.output(in2, GPIO.LOW)
            GPIO.output(in3, GPIO.LOW)
            
            GPIO.output(in1, GPIO.HIGH)
            GPIO.output(in2, GPIO.HIGH)
            sleep(impulse_timeout)
            GPIO.output(in1, GPIO.LOW)
            GPIO.output(in2, GPIO.LOW)

def openDrop():
    pwm = GPIO.PWM(dropGPIO, 50)
    pwm.start(0)
    pwm.ChangeDutyCycle(11)
    sleep(0.525)
    pwm.stop()

def closeDrop():
    pwm = GPIO.PWM(dropGPIO, 50)
    pwm.start(0)
    pwm.ChangeDutyCycle(7.3)
    sleep(0.525)
    pwm.stop()

def rotate(angle):
    steps = int(512 * abs(angle) / 360)
    print(steps)
    if angle >= 0:
        forward(steps)
        sleep(1)
        openDrop()
        sleep(2)
        closeDrop()
        sleep(1)
        backward(steps)
    else:
        backward(steps)
        sleep(1)
        openDrop()
        sleep(2)
        closeDrop()
        sleep(1)
        forward(steps)
        
        
def classifyGarbage(path = 'image.jpg'):
    interpreter = tflite.Interpreter(model_path="model.tflite")
    interpreter.allocate_tensors()

    # Get input and output tensors.
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    # Test the model on random input data.
    input_shape = input_details[0]['shape']
    
    img = load_img(path)
    img = img.crop(genBox(resX, resY, boxSide))
    img.save('/home/pi/Downloads/imageCropped.jpg')
    img = img.resize((300,300))
    arr = img_to_array(img)
    arr = np.expand_dims(arr, 0)

    input_data = np.array(np.random.random_sample(input_shape), dtype=np.float32)
    interpreter.set_tensor(input_details[0]['index'], arr)

    interpreter.invoke()

    output_data = interpreter.get_tensor(output_details[0]['index'])
    return np.argmax(output_data)

def drop(label = 5):
    print(labelToString[label])
    mqttc.publish("bin/", labelToString[label], 0, False)
    rotate(labelToAngle[label])

mqttc = mqtt.Client()
mqttc.connect("localhost", 1883, 60)
        
camera = picamera.PiCamera()
camera.resolution = (resX, resY)

while True:
     input_state = GPIO.input(buttonGPIO)
     if input_state == False:
          print('Button Pressed')
          camera.start_preview()
          sleep(2)
          camera.capture('/home/pi/Downloads/image.jpg')
          camera.stop_preview()
          drop(classifyGarbage())
          
camera.stop_preview()
          
GPIO.cleanup()
