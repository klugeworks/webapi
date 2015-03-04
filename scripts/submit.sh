#!/usr/bin/bash

name=$1
queue=$2
filepath=$3
webser

curl -v -F "name=$name" -F "queue=$queue" -F "bytes=@$filepath" http://127.0.0.1:5000/fileup