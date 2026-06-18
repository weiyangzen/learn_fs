# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevstc2.c

Floyd-Steinberg error diffusion dithering routines for the Epson Stylus Color driver.

Key behavior:
- Implements `stc_fs`, used for `fsmono`, `fsrgb`, and `fsx4`.
- Implements `stc_fscmyk`, a modified CMYK Floyd-Steinberg algorithm.
- Uses long-valued error buffers and serpentine scan direction.
- Converts component threshold decisions into driver output bit masks with lookup tables for gray, RGB, and CMYK.
- Initializes diffusion buffers, threshold, spot size, and optional randomized starting errors.
- `stc_fs` applies per-component Floyd-Steinberg diffusion for 1-, 3-, or 4-component data.
- `stc_fscmyk` treats black specially: black is evaluated first, and color firing behavior changes depending on whether black fired.
- Supports driver flags such as `Flag0` to disable randomized initialization and `Flag1` to alter CMYK threshold selection.

Notable dependencies:
- Shared Stylus Color definitions from `gdevstc.h`.
- Uses `rand()` from the C library.

Research notes:
- Comments note that `fsx4` gives poor results and `fscmyk` is algorithmically similar to `hscmyk` but slower.
- Both algorithms reject `STC_DIRECT` and `STC_WHITE`.
- Output is encoded in the Stylus Color driver’s local color-bit convention.
