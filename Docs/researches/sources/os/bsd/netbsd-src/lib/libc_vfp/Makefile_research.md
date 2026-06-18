# File Research: sources/os/bsd/netbsd-src/lib/libc_vfp/Makefile

## Purpose
Builds ARM VFP-backed libc floating-point helper library `libc_vfp`.

## Build Behavior
Sets `LIB=c_vfp`, enables shared-library directory placement, selects `vfpsf.S` and `vfpdf.S`, and includes `bsd.lib.mk`.

## Dependencies
Depends on ARM/VFP assembler support and NetBSD library make infrastructure.

## Risks And Notes
This library assumes a target context where VFP instructions are valid.
