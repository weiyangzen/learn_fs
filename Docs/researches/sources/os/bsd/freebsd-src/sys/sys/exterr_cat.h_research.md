# File Research: sources/os/bsd/freebsd-src/sys/sys/exterr_cat.h

## Purpose
Defines stable category identifiers for FreeBSD extended errors.

## Main Interfaces
- Category constants including mmap, filedesc, ktrace, FUSE paths, inotify, genio, bridge, swap, VFS syscall/bio, GEOM, fork, process exit, VMM, HWPMC IBS, and linker categories.
- Explicit guidance that IDs are ABI between kernel and libc and must never be reused or changed.

## Dependencies And Integration
Included by extended-error kernel and userland support. The comments identify a libc filename generation script that must be run when adding categories.

## Risk Notes
This is pure ABI. Only append new category IDs; do not renumber or reuse.
