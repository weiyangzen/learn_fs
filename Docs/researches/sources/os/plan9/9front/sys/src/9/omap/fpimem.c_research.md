# File Research: sources/os/plan9/9front/sys/src/9/omap/fpimem.c

Conversions between memory floating-point encodings and `Internal` soft-FP values.

Key behavior:
- `fpis2i` converts 32-bit single to `Internal`.
- `fpid2i` converts 64-bit double to `Internal`.
- `fpiw2i` converts integer word to `Internal`.
- `fpii2s` converts `Internal` to single.
- `fpii2d` converts `Internal` to double.
- `fpii2w` converts `Internal` to integer word.
- Handles sign, exponent bias adjustments, denormal-like low exponent cases, infinity, NaN, and zero.

Research notes:
- These routines are memory-format glue for `fpiarm.c` instruction emulation.
