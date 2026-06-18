# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/close.c

This is a code-generation helper for color quantization tables.

Key behavior:
- Converts YCbCr to approximate RGB and finds the nearest Plan 9 colormap index by squared RGB distance.
- Buckets colors into a 5-bit-per-component cube.
- Prints per-bucket colormap index lists.
- Intended to generate lookup data, not to operate as an image viewer/converter.

Research notes:
- This program is computationally heavy: it iterates all 256^3 Y/Cb/Cr combinations.
