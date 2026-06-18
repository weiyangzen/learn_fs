# File Research: sources/local-fs/e2fsprogs/e2fsck/e2fsck.c

## Purpose
Core lifecycle and pass dispatcher for an e2fsck run.

## Main Behavior
- `e2fsck_allocate_context()` allocates and initializes `struct e2fsck_struct`, setting defaults such as inode processing size, extended attribute version, page block count, HTREE slack, and current time. `E2FSCK_TIME` can override time for tests.
- `e2fsck_reset_context()` frees per-run bitmaps, dirinfo/dx-dirinfo, EA refcounts, encrypted-file info, invalid metadata flags, casefold maps, counters, journal I/O, and pass statistics.
- `e2fsck_free_context()` calls reset, releases blkid/profile/logging resources, closes problem XML logs, and frees the context.
- `e2fsck_run()` executes pass sequence: pass1, pass1e, pass2, pass3, pass4, pass5. It updates MMP before each pass and honors abort/restart/cancel flags.

## Integration
This is the control skeleton for all e2fsck passes. Most modules in this group allocate data into `e2fsck_t` fields and rely on reset/free to dispose of them.

## Risks / Notes
The context reset path is broad and central; leaked or stale per-pass state usually needs to be wired into this file.
