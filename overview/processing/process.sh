#!/usr/bin/env bash

set -euo pipefail
shopt -s nullglob

# --- Step 1: Convert .m4a → .mp3 ---
for file in *.m4a; do
    out="${file%.m4a}.mp3"
    echo "Converting $file → $out"
    ffmpeg -y -i "$file" -vn -c:a libmp3lame -b:a 192k "$out"
done

# --- Step 2: Move original .m4a files ---
if compgen -G "*.m4a" > /dev/null; then
    echo "Moving original .m4a files..."
    mv -- *.m4a ../../..
fi

# --- Step 3: Time/pitch transform ---
for f in *.mp3; do
    tmp="temp_$f"
    echo "Processing tempo/pitch for $f"
    if ffmpeg -y -i "$f" -filter_complex "asetrate=44100*0.900,atempo=0.94,aresample=44100" -q:a 0 "$tmp"; then
        mv -f "$tmp" "$f"
    else
        echo "Failed on $f"
        rm -f "$tmp"
    fi
done

# --- Step 4: Compress bitrate ---
for f in *.mp3; do
    tmp="compressed_$f"
    echo "Compressing $f"
    if ffmpeg -y -i "$f" -vn -c:a libmp3lame -b:a 64k "$tmp"; then
        mv -f "$tmp" "$f"
    else
        echo "Compression failed on $f"
        rm -f "$tmp"
    fi
done

echo "Done."
