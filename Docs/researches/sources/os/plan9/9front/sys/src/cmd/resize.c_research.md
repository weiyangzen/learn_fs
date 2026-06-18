# File Research: sources/os/plan9/9front/sys/src/cmd/resize.c

Simpler image resizer using bilinear interpolation by default and nearest-neighbor with `-n`.

Supports `-x`, `-y`, `-a`, absolute or percentage dimensions, stdin or one image file, and aspect-ratio preservation.

Like `resample.c`, converts unsupported channel formats through byte-per-channel temporary images and writes a Plan 9 memimage to stdout.
