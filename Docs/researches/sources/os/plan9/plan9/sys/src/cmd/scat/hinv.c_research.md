# File Research: sources/os/plan9/plan9/sys/src/cmd/scat/hinv.c

Implements the inverse H-transform used by DSS compressed image decoding.

Key functions:
- `hinv` iteratively expands wavelet/H-transform coefficients into pixel values for arbitrary image dimensions.
- `unshuffle` and `unshuffle1` deinterleave coefficient arrays along strided and contiguous dimensions.

Behavior notes:
- Handles odd image widths/heights separately while reconstructing 2x2 blocks.
- Allocates temporary storage sized to half the maximum dimension.
- Fatal memory allocation failure exits with `"memory"`.
