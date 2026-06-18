# File Research: sources/os/plan9/9front/sys/src/9/pc/hcwAMC.h

## Purpose
Defines a single static byte-array payload, `hcwAMC[]`, used as embedded firmware/microcode data by the PC TV driver path.

## Key Elements
The file is a large `static uchar hcwAMC[] = { ... };` initializer containing 2027 lines of hexadecimal byte data and no functions, macros, comments, or type declarations. A repository reference search shows `devtv.c` includes this header and passes `hcwAMC` plus `sizeof hcwAMC` to `kfirloadu(...)`, so the payload is loaded into the TV/KFir-related device path at runtime.

## Dependencies
Depends on the includer already defining `uchar`; it is meant to be included from C source rather than compiled independently.

## Behavior/Risks
This is opaque device data, not executable C logic. Review risk is mostly provenance and correctness of the blob: corruption, truncation, or unsigned-byte type changes would affect device initialization. Because it is `static`, each includer would get a private copy, but current use appears to be a direct include by `devtv.c`.
