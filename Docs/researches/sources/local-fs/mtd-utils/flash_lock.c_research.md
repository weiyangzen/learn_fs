# File Research: sources/local-fs/mtd-utils/flash_lock.c

## Purpose
Builds the locking variant of the shared flash lock/unlock utility.

## Key Elements
Defines `PROGRAM_NAME` as `flash_lock` and includes `flash_unlock.c`, causing the shared code to compile with `FLASH_UNLOCK` set to `0` and use `MEMLOCK`.

## Dependencies
Depends entirely on `flash_unlock.c` implementation and MTD lock ioctl support.

## Behavior/Risks
This include-based reuse is intentional but fragile: macro state before inclusion determines whether the compiled utility locks or unlocks.
