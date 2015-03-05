#!/bin/bash

audio_split_dir=$1
kluge_server=$2
podcast_name=$(basename $audio_split_dir)

chunkid=1
for audio in $(ls $audio_split_dir/*.ul | sort); do
    basen=$(basename $audio);
    echo "$basen:$chunkid";
    curl -F "docid=$podcast_name" -F "chunkid=$chunkid" -F "name=$basen" -F "bytes=@$audio" http://$kluge_server/jobs/english
    chunkid=$((chunkid + 1));
done
