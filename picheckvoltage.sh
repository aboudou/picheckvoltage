#!/bin/sh
# 
# Start / Shutdown script for PiCheckVoltage 
#

DIR=$(cd $(dirname "$0"); pwd)

case "$1" in
  start)

    # Start PiCheckVoltage
    `which python` "${DIR}"/main.py &

    ;;
  stop)
    # Stop PiCheckVoltage
    if [ -f /var/run/picheckvoltage.pid ]
    then
      `which kill` `cat /var/run/picheckvoltage.pid`
      `which rm` /var/run/picheckvoltage.pid
    fi

    ;;

  *)
    echo "Usage: $0 {start|stop}" >&2
    exit 1

    ;;

esac

exit 0
