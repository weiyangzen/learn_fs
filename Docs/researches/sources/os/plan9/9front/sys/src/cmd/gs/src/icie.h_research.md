# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/icie.h

Declares internal interpreter helpers for CIE color spaces and rendering dictionaries.

Key points:
- Provides dictionary parameter readers for ranges, 3-range sets, 3x3 matrices, procedure arrays, 3-procedure arrays, WhitePoint/BlackPoint, and lookup tables.
- Declares `cie_set_finish` for completing color-space setup.
- Declares cache preparation helpers that sample PostScript procedures into CIE caches via continuations.
- Provides macros for 3- and 4-component cache preparation.
- Declares `cie_cache_joint`, used between CIE color space and color rendering dictionary setup.

Research notes:
- These APIs bridge PostScript dictionary/procedure data into graphics-library CIE color caches.
- Many functions are exported between `zcie.c` and `zcrd.c`.
