# File Research: sources/local-fs/xfsprogs/repair/globals.h

## Role

`globals.h` declares shared constants, global variables, and quota inode helpers for xfs_repair.

## Constants

- `XR_*` superblock and geometry error codes.
- Legal filesystem block-size log bounds.
- `NUM_AGH_SECTS`, the expected number of AG header sectors.
- `ORPHANAGE`, the lost+found directory name.
- `rounddown` utility macro.

## Global Declarations

The header exposes all shared state defined in `globals.c`, plus:

- `rt_lock`, used for legacy realtime extent map protection.
- `struct libxfs_init x`, the global libxfs initialization descriptor.
- Feature-upgrade booleans such as `add_bigtime`, `add_nrext64`, and `add_exchrange`.

## Quota API

Declares helpers to set, clear, lose, read, and test quota inode numbers.

## Interactions

Almost every file in this group includes `globals.h` because repair phases are coordinated through shared mode flags, feature flags, counters, and reconstruction markers.
