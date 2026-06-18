# File Research: sources/os/plan9/9front/sys/src/cmd/scat/hinv.c

Purpose: Performs inverse H-transform expansion for DSS image tiles.

Key routines:
- `hinv`: calculates rounded-up transform depth, repeatedly unshuffles coefficients in both dimensions, then reconstructs pixel values from H-transform components.
- `unshuffle`: interleaves half-array coefficients for strided 2D access.
- `unshuffle1`: optimized 1D unshuffle.

Integration: Called after q-tree and sign-bit decoding in `dssread.c`.

Risks:
- Uses integer shift/rounding assumptions from the DSS compression format.
- Allocates temporary storage sized by the larger image dimension and exits on allocation failure.
- Handles odd row/column dimensions explicitly.
