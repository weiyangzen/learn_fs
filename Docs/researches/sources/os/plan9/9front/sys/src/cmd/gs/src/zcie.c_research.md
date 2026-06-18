# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zcie.c

This file implements CIE color-space operators and the procedure-cache setup needed by CIE spaces.

Key behavior:
- Provides dictionary parameter helpers for ranges, 3x3 matrices, procedure arrays, white/black points, and lookup tables.
- Validates CIE white/black points and lookup table dimensions/string sizes.
- Implements `.setcieaspace`, `.setcieabcspace`, `.setciedefspace`, and `.setciedefgspace`.
- Builds CIE color spaces using graphics-library constructors, fills parameter structures, installs cached decode procedures, and calls `gs_setcolorspace`.
- Uses e-stack continuations to sample PostScript decode procedures into fixed-size CIE caches before completing color-space setup.
- Provides shared cache preparation and completion routines for one, three, or four decode procedures.

Important dependencies:
- Uses CIE color structures from `gscie.h`, `gscolor2.h`, and `gxcspace.h`.
- Uses interpreter procedure execution through `zfor_samples`, `zcvx`, and e-stack continuations.
- Stores active CIE procedure refs in `istate->colorspace.procs.cie`.

Research notes:
- This file is interpreter-to-graphics-library glue for calibrated color spaces.
- It is sensitive to e-stack cleanup because setup can partially allocate color spaces and cache tables before errors.
