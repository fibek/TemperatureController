#!/bin/sh

# /etc/init.d/init.sh
### BEGIN INIT INFO
# Provides:          init.sh
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description:
# Description:       Start temperature controller and its server
### END INIT INFO

(cd ~/TemperatureController ; python3 tempcontroller.py 2>&1 > /dev/null &)
(cd ~/TemperatureController ; uvicorn server:app --host 0.0.0.0 --port 8000 2>&1 > /dev/null  &)

