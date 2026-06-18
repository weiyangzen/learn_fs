# File Research: sources/os/bsd/netbsd-src/lib/librumpvfs/Makefile

## Purpose
Builds the `librumpvfs` rump VFS library by delegating to the rump kernel makefile fragment.

## Key Elements
Sets `NOFULLRELRO=yes`, defines `RUMPTOP=${.CURDIR}/../../sys/rump`, adds a dependency library on `librump`, sets `WARNS=3`, and includes `${RUMPTOP}/librump/rumpvfs/Makefile.rumpvfs`.

## Dependencies
Depends on NetBSD make infrastructure, `bsd.lib.mk` indirectly through the included rump makefile, and the source tree under `sys/rump`.

## Risks And Notes
The file is intentionally thin; most build behavior is inherited. The warning level is capped because kernel code is not ready for stricter sign-compare warnings.
