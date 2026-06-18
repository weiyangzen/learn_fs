# File Research: sources/os/plan9/9front/sys/src/cmd/audio/scream/screamenc.c

Encoder for wrapping raw PCM into Scream packet framing.

Key responsibilities:
- Uses fixed defaults: 44.1 kHz, stereo, 16-bit PCM, and 5 ms packet delay.
- Builds the 5-byte Scream header from rate multiplier, bits per sample, and channel count.
- Reads frame-sized chunks from stdin and writes header plus payload to stdout.

Research notes:
- There are no command-line options; globals are compile-time defaults.
- Intended to be paired with `/dev/audio` and the `screamsend` wrapper.
