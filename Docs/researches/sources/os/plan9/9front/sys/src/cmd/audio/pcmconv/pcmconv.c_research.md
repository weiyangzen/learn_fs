# File Research: sources/os/plan9/9front/sys/src/cmd/audio/pcmconv/pcmconv.c

Generic PCM format conversion command.

Key responsibilities:
- Parses input/output PCM descriptors with `-i fmt` and `-o fmt`; defaults both from `pcmdescdef`.
- Accepts optional byte length limit through `-l length`.
- Allocates a conversion context with `allocpcmconv()`.
- Computes output buffer sizing via `pcmratio()`.
- Streams stdin through `pcmconv()` and writes converted audio to stdout.

Dependencies:
- Uses Plan 9 `pcm.h` conversion API.

Research notes:
- The loop stops when `pcmconv()` returns zero, which may follow EOF or converter drain behavior.
- Length limiting is byte-based on input reads.
