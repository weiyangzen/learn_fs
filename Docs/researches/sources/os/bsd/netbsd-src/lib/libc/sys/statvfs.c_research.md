# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/statvfs.c

## Purpose
Provides default waiting variants of VFS stat calls.

## Key Elements
Maps `statvfs`, `fstatvfs`, and `fhstatvfs` to their `*vfs1` variants with `ST_WAIT`.

## Dependencies
Uses `<sys/statvfs.h>` and `statvfs1`, `fstatvfs1`, `fhstatvfs1`.

## Behavior/Risks
All semantics are delegated to `*vfs1`; the wrapper fixes the wait/non-wait flag to `ST_WAIT`.
