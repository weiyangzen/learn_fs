# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevstc2.c

Purpose: Floyd-Steinberg error diffusion algorithms for the Epson Stylus Color driver.

Key behavior:
- Provides `stc_fs` for gray/RGB/CMYK-style per-component Floyd-Steinberg dithering using long error buffers.
- Converts internal bit decisions to driver output bytes with gray, RGB, or CMYK conversion tables.
- Alternates scan direction forward/backward using buffer state.
- Initializes threshold, spot size, and randomized or zeroed error buffers depending on `Flag0`.
- Provides `stc_fscmyk`, a modified CMYK algorithm that handles black first, then colors differently depending on whether black fires.
- `stc_fscmyk` validates four components, long data, sufficient buffer, and no direct/white flags.

Important dependencies:
- `gdevstc.h`, plus `rand()` from `<stdlib.h>`.

Notable risks / findings:
- Randomized initial error state means output can depend on C library RNG state unless `Flag0` disables it.
- CMYK behavior is specialized and documented as experimental/bad for some modes in the comments.
