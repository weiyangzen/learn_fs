# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevstc4.c

Alternative byte-based Floyd-Steinberg-style RGB dithering module for the Epson Stylus Color driver.

Key behavior:
- Implements `stc_fs2`, selected with `-sDithering=fs2`.
- Adapts Steven Singer’s `escp2cfs2` algorithm.
- Maintains a byte error buffer for RGB scanline diffusion.
- Clears error state on white-line notifications.
- Applies accumulated signed byte errors to incoming RGB values, clamping to 0..255.
- Chooses the nearest printable RGB cube color using `escp2c_pick_best`, which uses a custom weighted distance metric rather than simple Euclidean distance.
- Alternates scan direction with a static `dir` variable.
- Diffuses errors to neighboring and next-line positions.
- Converts selected RGB triplets into the Stylus Color packed output bit format.
- Initialization validates RGB, byte-mode, and sufficient scanline buffer count.

Notable dependencies:
- Shared Stylus Color definitions from `gdevstc.h`.

Research notes:
- The custom color-distance logic is designed to reduce unwanted colored artifacts in gray regions.
- `dir` is static at function scope, so scan direction is shared across device invocations.
- This file contains only the dither algorithm, not printer command output.
