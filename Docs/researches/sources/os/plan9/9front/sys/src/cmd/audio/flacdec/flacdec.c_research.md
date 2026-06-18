# File Research: sources/os/plan9/9front/sys/src/cmd/audio/flacdec/flacdec.c

FLAC decoder front-end adapted for Plan 9 audio pipelines.

Important behavior:
- Uses libFLAC stream-decoder callbacks reading from standard input.
- Supports seeking with `-s seconds` by decoding enough metadata to obtain sample rate, then seeking by sample number.
- Converts decoded per-channel FLAC samples into interleaved PCM bytes.
- Starts `/bin/audio/pcmconv -i <fmt>` when sample format changes, piping PCM through it.
- Can suppress output during seek pre-roll.

It depends on the bundled/ported libFLAC API plus Plan 9 libc compatibility headers.
