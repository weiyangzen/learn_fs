# File Research: sources/os/plan9/9front/sys/src/cmd/audio/scream/screamdec.c

Decoder for Scream network audio packets.

Key responsibilities:
- Reads packets containing a 5-byte Scream header plus PCM payload from stdin.
- Decodes sample rate, bit depth, and channel count into a Plan 9 PCM format string.
- Starts `/bin/audio/pcmconv` only when the stream format differs from default `s16c2r44100`.
- Restarts the converter when packet format changes.
- Writes payload audio to either stdout or the converter pipe.

Dependencies:
- Uses `/bin/audio/pcmconv` for non-default PCM conversion.

Research notes:
- Uses a short alarm around reads, making it suited to live network streams.
- Packet header comparison drives converter restart.
