# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/inflate.c

## Purpose
Boot-kernel wrapper that includes gzip/deflate support.

## Main Interfaces
- Compiles `inflate.guts.c` into the boot environment.

## Implementation Notes
- Includes kernel/boot headers and `<flate.h>`.
- The actual `gunzip` implementation and helpers live in `inflate.guts.c`.

## Dependencies And Risks
- This file is mostly a compilation-context shim; behavior depends on included code.
