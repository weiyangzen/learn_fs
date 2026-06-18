# File Research: sources/os/plan9/9front/sys/src/cmd/gs/zlib/zconf.h

## Purpose
Installed zlib configuration header for portability, symbol naming, calling conventions, and core zlib types.

## Key Elements
Defines optional `Z_PREFIX` symbol remapping, platform detection macros, `MAX_MEM_LEVEL`, `MAX_WBITS`, function prototype macro `OF`, calling/export macros `ZEXTERN`, `ZEXPORT`, `ZEXPORTVA`, `FAR`, core typedefs (`Byte`, `uInt`, `uLong`, `Bytef`, `voidpf`, etc.), `z_off_t`, and special mappings for Windows, BeOS, OS/400, and MVS.

## Behavior/Risks
This header is foundational: changing macros can alter public ABI, memory requirements, exported symbol names, and wrapper behavior. `HAVE_UNISTD_H` is represented by a configure-updated `#if 0` block in this copy, so `z_off_t` defaults to `long`. It is identical to `zconf.in.h` except for the source-control identification line.

## Dependencies
Included by `zlib.h` and other zlib headers. Supplies portability definitions used throughout this zlib subtree.
