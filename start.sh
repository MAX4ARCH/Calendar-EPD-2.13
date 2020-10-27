#!/bin/bash

t="$1"
if [ "$t" = "r" ];then
echo "rebooting in 30 sec"
screen -S "monitor" -p 0 -X stuff "^C" && sleep 30 && sudo reboot
elif [ "$t" = "rt" ];then
if screen -list | grep -q "monitor"; then
echo "waiting in 30 sec"
screen -S "monitor" -p 0 -X stuff "^C" && sleep 30 && if ! screen -list | grep -q "monitor"; then screen -S "monitor" -dm python3 max.py; fi && exit
else
screen -S "monitor" -dm python3 max.py && exit
fi
elif [ "$t" = "s" ];then
echo "Stopping"
screen -S "monitor" -p 0 -X stuff "^C"
ps -ef | grep 'start.sh' | grep -v grep | awk '{print $2}' | xargs -r kill -9
fi

up=$(uptime | awk -F'( |,|:)+' '{d=h=m=0; if ($7=="min") m=$6; else {if ($7~/^day/) {d=$6;h=$8;m=$9} else {h=$6;m=$7}}} {print m+0}')
if [ "$up" -gt "4" ] ; then
if ! screen -list | grep -q "monitor"; then
screen -S "monitor" -dm python3 max.py && exit
fi
else
sleep 240 && if ! screen -list | grep -q "monitor"; then screen -S "monitor" -dm python3 max.py; fi
#chk=1
#while [ "$chk" -eq "1" ]; do
#wget -q --spider http://google.com
#chk="$?"
#sleep 60; done && if ! screen -list | grep -q "monitor"; then screen -S "monitor" -dm python3 max.py; fi
fi

count=1
while true; do
#echo "loop"
 if ! screen -list | grep -q "monitor"; then
  wget -q --spider http://google.com
  if [ "$?" -eq "0" ] ; then
   screen -S "monitor" -dm python3 max.py
  fi
 fi
  #echo "count:$count" >> log.txt
  if [ "$count" -eq "18" ] ; then
   sleep 120 && screen -S "monitor" -p 0 -X stuff "^C" && sleep 30 && if ! screen -list | grep -q "monitor"; then screen -S "monitor" -dm python3 max.py; fi
   count=1
  fi
  count=$((count+1))
sleep 600; done
