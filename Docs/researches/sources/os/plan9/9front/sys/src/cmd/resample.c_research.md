# File Research: sources/os/plan9/9front/sys/src/cmd/resample.c

Image resizer using Plan 9 `memdraw`. Implements separable resampling with a precomputed Kaiser-windowed kernel.

Supports `-x`, `-y`, and compatibility `-a` dimensions, with integer or percentage values. Preserves aspect ratio when only one dimension is supplied.

Handles common byte-per-channel formats directly and converts indexed/packed or alpha-containing images to suitable temporary formats before converting back.
