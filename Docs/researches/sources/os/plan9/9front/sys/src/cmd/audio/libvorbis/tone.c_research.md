# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/tone.c

Small standalone tone generator utility.

Important contents:
- Parses command-line arguments as `<frequency_Hz>[,<amplitude>]`.
- Allocates frequency/amplitude arrays with `alloca()`.
- Generates 10 seconds of 44.1 kHz stereo 16-bit little-endian PCM to stdout.
- Sums sine waves, rounds with `rint()`, clips to signed 16-bit range, and writes duplicate left/right samples.
- `usage()` prints syntax and exits.

Integration points:
- Not tied into libvorbis internals; uses only C library math/stdio/string/stdlib.
- Useful for generating simple test tones.

Risk and review signals:
- Uses `alloca()` without including an explicit alloca header in this file.
- Writes raw PCM, not WAV with headers.
- No argument validation beyond `atof()` conversion.
- Long argument lists can consume stack.

Filesystem relevance:
- No filesystem implementation. It writes generated audio bytes to stdout.
