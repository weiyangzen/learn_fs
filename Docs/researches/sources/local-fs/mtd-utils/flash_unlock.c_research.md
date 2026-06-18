# File Research: sources/local-fs/mtd-utils/flash_unlock.c

## Purpose
Shared implementation for `flash_unlock` and, when included by `flash_lock.c`, `flash_lock`.

## Key Elements
Parses `<mtd device> [offset] [block count]`, reads device size and erase size using `MEMGETINFO`, validates range, and issues either `MEMUNLOCK` or `MEMLOCK` depending on compile-time macros.

## Dependencies
Uses `common.h` and `mtd/mtd-user.h`.

## Behavior/Risks
Offset and count parsing uses `strtol` without full validation. A block count of `-1` means the entire device.
