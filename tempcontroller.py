#!/bin/env python3
# import w1thermsensor
# import RPi.GPIO as GPIO
# import PID
import time

import os
import zmq
import signal

# COOLING = 17 # cooling device pin
# HEATING = 22 # heater device pin

# GPIO.setmode(GPIO.BCM)
# GPIO.setwarnings(False)

# GPIO.setup(COOLING, GPIO.OUT) # cooler
# GPIO.output(COOLING, GPIO.LOW)

# GPIO.setup(HEATING, GPIO.OUT) # heating
# GPIO.output(HEATING, GPIO.LOW)

# sensor = w1thermsensor.W1ThermSensor()
# temperature = sensor.get_temperature()
# print("Current temperature: ",temperature)

T = 31.0
P = 1.4
I = 1
D = 0.001
ST = 15 # SampleTime
# pid = PID.PID(P, I, D)

# pid.SetPoint = T
# pid.setSampleTime(ST)

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")
hello = socket.recv()
if(hello == b'hello'):
    processid = os.getpid()
    socket.send(str(processid).encode());

def handler1(signal, frame):
    try: 
        q = socket.recv().decode().split('|')
        global T,P,I,D,ST
        T,P,I,D,ST = q
        print(T,P,I,D,ST)
        pid.SetPoint = T
        pid.setKp(P)
        pid.setKi(I)
        pid.setKd(D)
        pid.setSampleTime(ST)
        socket.send(b'ok')
    except:
        socket.send(b'error')

def handler2(signal, frame):
    try:
        print(socket.recv().decode())
        socket.send(f'{CT}|{T}|{P}|{I}|{D}|{ST}'.encode('UTF-8'))
    except:
        socket.send(b'error')

signal.signal(signal.SIGUSR1, handler1)
signal.signal(signal.SIGUSR2, handler2)

print('PID controller is running..')
try:
    feedback = 0
    while 1:
        pid.update(feedback)
        output = pid.output
        try:
            temperature = sensor.get_temperature()
        except:
            time.sleep(0.5)
            temperature = sensor.get_temperature()

        print('TEMPERATURE: ',temperature)
        if temperature is not None:
            if pid.SetPoint > 0:
                feedback += temperature + output

            print(f'desired.temp={pid.SetPoint:0.1f}*C temp={temperature:0.1f}*C pid.out={output:0.1f} feedback={feedback:0.1f}')
            if output > 0:
                print('turn on heater')
                # GPIO.output(COOLING, GPIO.LOW)
                # GPIO.output(HEATING, GPIO.HIGH)
            elif output < 0:
                print('turn on cooler')
                # GPIO.output(HEATING, GPIO.LOW)
                # GPIO.output(COOLING, GPIO.HIGH)


        time.sleep(0.5)

except KeyboardInterrupt:
    print("exit")
    GPIO.cleanup()

