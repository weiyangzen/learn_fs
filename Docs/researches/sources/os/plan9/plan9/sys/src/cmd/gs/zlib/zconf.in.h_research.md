# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/zconf.in.h

## Purpose
Template/configuration-source version of `zconf.h`. It contains the same portability and type-definition logic, intended to be processed or copied by zlib configuration workflows.

## Major Features
Matches `zconf.h` in:
- Optional `Z_PREFIX` symbol/type renaming.
- Platform/compiler detection.
- `MAX_MEM_LEVEL` and `MAX_WBITS` defaults.
- Function prototype and calling convention macros.
- Basic zlib typedefs.
- `z_off_t` selection and seek constant fallbacks.
- Windows, BeOS, OS/400, and MVS branches.

## Difference from `zconf.h`
The observed content is functionally identical to `zconf.h`; the visible difference is the source identification comment:
- `zconf.h` identifies itself as `zconf.h`.
- `zconf.in.h` identifies itself as `zconf.in.h`.

## Usage
Kept as an input/template header for generated or configured builds. In this repository’s vendored Ghostscript zlib copy, it documents the same portability assumptions as the active `zconf.h`.
