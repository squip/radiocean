#!/bin/bash

cd /home/essorensen/radioscribe/app/static/audio_segments
python -m SimpleHTTPServer 8000 &>> ~/radioscribe/log/audio_segments_http.log &
echo "Started http server with PID $!"

