# File Research: sources/os/plan9/9front/sys/src/cmd/audio/flacenc/flacenc.c

FLAC encoder front-end for Plan 9 audio pipelines.

Important behavior:
- Reads raw PCM from stdin and writes FLAC to stdout through libFLAC stream encoder callbacks.
- Parses input format with `-i`, including sample rate, channels, sample bits, and endian choice.
- Supports compression level `-l`, padding metadata `-P`, and Vorbis comment tags `-T field=value`.
- Converts packed PCM bytes into signed `FLAC__int32` interleaved samples.
- Initializes encoder metadata and streams until stdin EOF.

This is a focused adapter between Plan 9 audio format strings and libFLAC encoding.
