# File Research: sources/local-fs/jfsutils/libfs/libjufs.h

## Purpose
Defines shared libfs error return constants for JFS utility callers.

## Constants
- `LIBFS_BADMAGIC` = `-5`: unrecognized magic number.
- `LIBFS_BADVERSION` = `-6`: magic recognized but version incompatible.
- `LIBFS_CORRUPTSUPER` = `-10`: invalid fragment size, allocation group size, or IAG size in the superblock.

## Notes
This is a small status-code header with no dependencies. The negative values are intended to distinguish libfs validation failures from normal system `errno` values.
