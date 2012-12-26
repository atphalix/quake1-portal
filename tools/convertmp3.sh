#!/bin/sh
# Recursively convert all *.mp3 into *.wav

for file in *.mp3; do
    ffmpeg -i "$file" "`basename $file .mp3`.wav"
done

