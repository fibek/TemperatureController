#!/bin/env python3
import w1thermsensor
import RPi.GPIO as GPIO
import PID
import time
import json
import os
import zmq
import signal

COOLING = 17 # cooling device pin
HEATING = 22 # heater device pin

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(COOLING, GPIO.OUT) # cooler
GPIO.output(COOLING, GPIO.LOW)

GPIO.setup(HEATING, GPIO.OUT) # heating
GPIO.output(HEATING, GPIO.LOW)

sensor = w1thermsensor.W1ThermSensor()
temperature = sensor.get_temperature()
print("Current temperature: ",temperature)

try:
    with open('config.json') as f:
        data = json.load(f)
        T  = float(data['params']['T'])
        P  = float(data['params']['P'])
        I  = float(data['params']['I'])
        D  = float(data['params']['D'])
        ST = int(data['params']['ST'])
        f.close()
except:
    T = 31.0
    P = 0.4
    I = 1
    D = 0.001
    ST = 15 # SampleTime

pid = PID.PID(P, I, D)

pid.SetPoint = T
pid.setSampleTime(ST)

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")
hello = socket.recv()
if(hello == b'hello'):
    processid = os.getpid()
    socket.send(str(processid).encode());

def dumptofile():
    data = {
      "params": {
        "T": T,
        "P": P,
        "I": I,
        "D": D,
        "ST": ST
      }
    }
    try:
        with open('config.json','w') as f:
            f.write(json.dumps(data))
            f.close()
    except:
        pass

def handler1(signal, frame):
    try: 
        q = socket.recv().decode().split('|')
        global T,P,I,D,ST
        T,P,I,D,ST = q
        print(T,P,I,D,ST)
        pid.SetPoint = float(T)
        pid.setKp(float(P))
        pid.setKi(float(I))
        pid.setKd(float(D))
        pid.setSampleTime(int(ST))
        dumptofile()
        socket.send(b'ok')
    except:
        socket.send(b'error')

def handler2(signal, frame):
    try:
        print(socket.recv().decode())
        socket.send(f'{temperature}|{T}|{P}|{I}|{D}|{ST}'.encode('UTF-8'))
    except:
        socket.send(b'error')

signal.signal(signal.SIGUSR1, handler1)
signal.signal(signal.SIGUSR2, handler2)

print('PID controller is running..')
try:
    while 1:
        try:
            temperature = sensor.get_temperature()
        except:
            continue

        if temperature is not None:
            pid.update(temperature)
            output = pid.output
            print(f'SetPoint={pid.SetPoint:0.1f}*C MeasuredTemp={temperature:0.1f}*C pid.out={output:0.1f}')
            if output > 0:
                print('turn on heater')
                GPIO.output(COOLING, GPIO.LOW)
                GPIO.output(HEATING, GPIO.HIGH)
            elif output < 0:
                print('turn on cooler')
                GPIO.output(HEATING, GPIO.LOW)
                GPIO.output(COOLING, GPIO.HIGH)


        time.sleep(0.5)

except KeyboardInterrupt:
    print("exit")
    GPIO.cleanup()

