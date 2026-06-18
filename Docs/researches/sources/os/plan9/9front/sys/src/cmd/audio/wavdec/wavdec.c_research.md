# File Research: sources/os/plan9/9front/sys/src/cmd/audio/wavdec/wavdec.c

WAV/RIFF decoder front-end that parses headers and delegates sample conversion to `pcmconv`.

Key responsibilities:
- Validates `RIFF`/`WAVE` headers.
- Iterates chunks until `fmt ` and `data` are found, skipping unknown chunks.
- Parses PCM format, channels, rate, frame size, and bit depth.
- Maps WAV format codes for PCM, IEEE float, A-law, and u-law into Plan 9 PCM descriptors.
- Supports `-s SECONDS` by seeking within data based on rate and frame size.
- Executes `/bin/audio/pcmconv -i fmt -l data_len`.

Dependencies:
- Uses `/bin/audio/pcmconv`.

Research notes:
- Seeking is done by byte offset on stdin and only works on seekable inputs.
- The expression used to align seek offset depends on `wav.framesz`.
