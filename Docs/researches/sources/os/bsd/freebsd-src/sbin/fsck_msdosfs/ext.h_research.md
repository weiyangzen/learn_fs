# File Research: sources/os/bsd/freebsd-src/sbin/fsck_msdosfs/ext.h

## Purpose

Public internal header for `fsck_msdosfs`, declaring global options, return-state flags, opaque FAT descriptor accessors, and cross-file functions.

## Key Globals

- `alwaysno`, `alwaysyes`
- `preen`
- `rdonly`
- `skipclean`
- `allow_mmap`

## Return Flags

- `FSOK`
- `FSBOOTMOD`
- `FSDIRMOD`
- `FSFATMOD`
- `FSERROR`
- `FSFATAL`
- `FSDIRTY`

## Declared Interfaces

Includes functions from:
- `main.c`: `ask()`
- `check.c`: `checkfilesys()`
- `boot.c`: `readboot()`, `writefsinfo()`
- `fat.c`: dirty flag handling, FAT read/write, cluster get/set, chain checks, lost-chain scan
- `dir.c`: directory section lifecycle, tree scan, reconnect helpers

## Integration Notes

Uses an opaque `struct fat_descriptor` to keep FAT implementation details private to `fat.c` while exposing enough operations for directory checking.
