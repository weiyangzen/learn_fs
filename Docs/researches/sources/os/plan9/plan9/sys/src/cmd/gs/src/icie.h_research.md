# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/icie.h

Internal CIE color handling interface. It mostly exports parameter acquisition helpers from `zcie.c` to `zcrd.c`, plus cache coordination in the other direction.

Capabilities:
- Read range arrays, 3-ranges, 3x3 matrices, procedure arrays, WhitePoint/BlackPoint, and lookup tables from dictionaries.
- Finish CIE color space setup.
- Prepare sampled procedure caches for 1/3/4 component CIE transforms.
- Join CIE render caches with graphics state.

This is color-management support for interpreter-level CIE color spaces.
