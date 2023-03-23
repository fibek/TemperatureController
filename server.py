from fastapi import Body,FastAPI,HTTPException
from typing import Annotated
from pydantic import BaseModel
import zmq
import os
from signal import SIGUSR1
from signal import SIGUSR2

context = zmq.Context()
app = FastAPI()

socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")
socket.send(b'hello')
pid = int(socket.recv().decode())

class PIDparams(BaseModel):
    temp: float | None = 19.0
    p: float | None = 1.4
    i: float | None = 1
    d: float | None = 0.001
    st: int | None = 15

@app.put("/pid/set")
async def setparams(params: Annotated[PIDparams, Body(embed=True)]):
    try:
        os.kill(pid,SIGUSR1)
        socket.send(str(f'{params.temp}|{params.p}|{params.i}|{params.d}|{params.st}').encode())
    except:
        raise HTTPException(status_code=404, detail="Unexpected error")
    if socket.recv() == b'ok':
        return {"status": "OK"}
    else:
        raise HTTPException(status_code=404, detail="No response from temperature controller")

@app.get("/pid/status")
async def getstatus():
    try:
        os.kill(pid,SIGUSR2)
        socket.send(b'sig2')
        r = socket.recv().decode().split('|')
        return {
                    "Temperature":r[0],
                    "P":r[1],
                    "I":r[2],
                    "D":r[3],
                    "SampleTime":r[4]
                }
    except:
        raise HTTPException(status_code=404, detail="Unexpected error")
    
