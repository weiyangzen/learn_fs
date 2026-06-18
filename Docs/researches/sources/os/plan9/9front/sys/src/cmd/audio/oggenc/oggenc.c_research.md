# File Research: sources/os/plan9/9front/sys/src/cmd/audio/oggenc/oggenc.c

Simple libvorbis encoder example command.

Key responsibilities:
- Reads hardcoded stereo 16-bit 44.1 kHz raw PCM from stdin.
- Initializes Vorbis VBR encoding at quality `0.5`.
- Emits Vorbis identification/comment/codebook headers with page flushing.
- Converts little-endian interleaved signed PCM into float analysis buffers.
- Runs Vorbis analysis/bitrate packet flushing and writes Ogg pages to stdout.
- Cleans all Ogg/Vorbis state on exit.

Dependencies:
- Uses `vorbis/vorbisenc.h`, libogg/libvorbis APIs, stdio, and time-based stream serial selection.

Research notes:
- Format is fixed; there are no command-line options for rate, channels, or quality.
- It is close to the upstream Xiph encoder example with minimal Plan 9 integration.
