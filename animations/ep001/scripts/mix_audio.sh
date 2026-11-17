#!/usr/bin/env bash
# Voice + ducked music + discreet SFX -> public/audio/mix.mp3 (70 s, ~-14 LUFS, true peak <= -1.5 dB)
set -euo pipefail
cd "$(dirname "$0")/../public/audio"
D=70
ffmpeg -y -v error \
 -i narration.mp3 -i music.mp3 -i impact.mp3 -i whoosh.mp3 -i tick.mp3 -i water.mp3 -i flip.mp3 \
 -filter_complex "
 [0:a]aresample=48000,pan=stereo|c0=c0|c1=c0,highpass=f=70,acompressor=threshold=-20dB:ratio=2.2:attack=8:release=120,volume=1.0,apad=whole_dur=$D[v];
 [v]asplit=2[vmix][vsc];
 [1:a]aresample=48000,atrim=0:$D,volume=0.62,afade=t=in:d=2,afade=t=out:st=66.5:d=3.5[m0];
 [m0][vsc]sidechaincompress=threshold=0.03:ratio=7:attack=40:release=450:makeup=1[mduck];
 [2:a]aresample=48000,volume=0.9,asplit=2[i1][i2];
 [i1]adelay=3050|3050[imp1];
 [i2]volume=0.55,adelay=65700|65700[imp2];
 [3:a]aresample=48000,volume=0.38,asplit=6[w1][w2][w3][w4][w5][w6];
 [w1]adelay=9200|9200[wa];[w2]adelay=24600|24600[wb];[w3]adelay=34600|34600[wc];[w4]adelay=42900|42900[wd];[w5]adelay=52400|52400[we];[w6]adelay=60100|60100[wf];
 [4:a]aresample=48000,aloop=loop=-1:size=2147483647,atrim=0:5,volume=0.5,afade=t=in:d=0.5,afade=t=out:st=4.2:d=0.8,asplit=2[t1][t2];
 [t1]adelay=20600|20600[tk1];[t2]adelay=63800|63800[tk2];
 [5:a]aresample=48000,aloop=loop=-1:size=2147483647,atrim=0:10.2,lowpass=f=900,volume=0.55,afade=t=in:d=1.5,afade=t=out:st=8.7:d=1.5,adelay=24700|24700[wat];
 [6:a]aresample=48000,volume=0.75,adelay=47000|47000[fl];
 [vmix][mduck][imp1][imp2][wa][wb][wc][wd][we][wf][tk1][tk2][wat][fl]amix=inputs=14:normalize=0:duration=longest,
 atrim=0:$D,loudnorm=I=-14:TP=-1.5:LRA=9[out]" \
 -map "[out]" -ac 2 -ar 48000 -c:a libmp3lame -b:a 256k mix.mp3
ffprobe -v error -show_entries format=duration -of csv=p=0 mix.mp3
ffmpeg -hide_banner -nostats -i mix.mp3 -af ebur128=peak=true -f null - 2>&1 | grep -E "I:|Peak:" | tail -2
