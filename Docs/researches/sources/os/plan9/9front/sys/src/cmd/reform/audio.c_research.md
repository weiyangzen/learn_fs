# File Research: sources/os/plan9/9front/sys/src/cmd/reform/audio.c

MNT Reform audio-control filesystem for an I2C codec. Programs codec registers through `#J/i2c3/i2c.1a.data` and exposes synthetic `/dev/audioctl` and `/dev/volume`.

Tracks master DAC, headphone, speaker, volume pairs, output on/off state, sample rate, and 3D setting. Supports reset, speed 44100/48000, 3d percentage, output toggles, and relative/absolute volume changes.

Can run once with `-1` to initialize hardware without mounting the 9P service.
