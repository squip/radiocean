#!/bin/bash

pgrep mongod > /dev/null

if [ $? -eq 0 ] ; then 
echo `date` "mongodb running"
else 
echo `date` "mongodb not running. restarting mongodb"
service mongodb start
fi
