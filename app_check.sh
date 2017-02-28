#!/bin/bash

pgrep -al python | grep run.py > /dev/null

if [ $? -eq 0 ] ; then 
echo `date` "radioscribe app running"
else 
echo `date` "radioscribe app not running. restarting radiscribe app"
nohup python /home/essorensen/radioscribe/radioscribe_app/run.py >> /var/log/app_output.log
fi
