# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdct.h

Private shared declarations and arithmetic helpers for JPEG forward and inverse DCT modules.

Key points:
- Defines `DCTELEM` sizing for 8-bit versus wider sample builds and method pointer types for integer and floating FDCTs.
- Documents the FDCT convention: signed inputs, outputs scaled by 8, and quantization performed by the DCT manager.
- Defines multiplier-table element types for slow integer, fast integer, and floating IDCT implementations.
- Provides `IDCT_range_limit` and `RANGE_MASK` used by IDCT routines for fast safe sample limiting.
- Declares all compiled FDCT/IDCT variants, including reduced-size 4x4, 2x2, and 1x1 IDCTs.
- Supplies fixed-point helper macros: `FIX`, `DESCALE`, and portable 16x16 multiply variants.

Dependencies and interactions:
- Included by `jcdctmgr.c`, `jddctmgr.c`, and individual DCT/IDCT algorithm files.
- Assumes common integer-shift behavior supplied by `jmorecfg.h`/platform configuration.

Risk notes:
- This is private infrastructure; using it outside DCT managers couples code to IJG internals.
- Compile-time feature macros must match the functions linked into the build.
- Arithmetic macro tuning affects performance and portability but not the public API shape.
