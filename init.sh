#!/bin/sh 

python3 tempcontroller.py &
uvicorn server:app --host 0.0.0.0 --port 8000 
