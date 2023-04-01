#!/bin/bash

# /etc/init.d/init.sh
### BEGIN INIT INFO
# Provides:          init.sh
# Required-Start:    $all 
# Required-Stop:     $all
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description:
# Description:       Start temperature controller and its server
### END INIT INFO

export PYTHONPATH=$PYTHONPATH:/home/pi/.local/lib/python3.9/site-packages
bash -c "(cd /home/pi/TemperatureController ; python3 tempcontroller.py 2>&1 > /dev/null &)"
bash -c "(cd /home/pi/TemperatureController ; uvicorn server:app --host 0.0.0.0 --port 8000 2>&1 > /dev/null  &)"

