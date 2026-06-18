# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevstc4.c

Purpose: Byte-oriented Floyd-Steinberg-style RGB dithering algorithm for `stcolor`, exposed as `fs2`.

Key behavior:
- Chooses nearest printable color among 8 RGB cube corners with a custom distance metric intended to avoid color artifacts in gray areas.
- Converts RGB triplets into `stcolor` bit-coded output bytes.
- Maintains byte error buffer and alternates direction between scanlines using a static `dir`.
- Handles white-line callbacks by clearing the error buffer.
- During processing, applies accumulated error to input, clamps values, selects nearest output color, diffuses error horizontally and to the next row, and writes compact output.
- Initialization validates RGB mode, byte algorithm type, and at least one scanline of buffer.

Important dependencies:
- `gdevstc.h`.

Notable risks / findings:
- Uses a static `dir`, so direction state is global across device instances/jobs rather than per-device.
- Mutates the input scanline buffer during dithering.
