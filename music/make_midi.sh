#!/usr/bin/bash

lilypond minuet.ly

timidity minuet.midi -Ow -o minuet.wav
ffmpeg -i minuet.wav -codec:a libmp3lame -qscale:a 2 minuet.mp3
