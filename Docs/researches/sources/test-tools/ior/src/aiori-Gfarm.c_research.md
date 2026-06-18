# sources/test-tools/ior/src/aiori-Gfarm.c

## Purpose
Implements an IOR backend for Gfarm using `gfs_pio_*` file APIs and Gfarm metadata/statfs functions.

## Important APIs, Types, and Functions
- `struct gfarm_file` wraps `GFS_File`.
- `Gfarm_initialize`/`Gfarm_finalize` call `gfarm_initialize` and `gfarm_terminate`.
- `Gfarm_create`, `Gfarm_open`, `Gfarm_xfer`, `Gfarm_close`, `Gfarm_delete`, and `Gfarm_fsync` wrap Gfarm PIO functions.
- `Gfarm_xfer` seeks once, then chunks transfers with a maximum request size of 1 GiB.
- Metadata callbacks convert `gfs_stat`, `gfs_statfs_by_path`, `gfs_mkdir`, and `gfs_rmdir` results into IOR/POSIX-like responses.

## Control Flow
After hints and initialization, create/open allocate a wrapper around the Gfarm file handle. Transfers seek to the requested offset and loop until the requested length is consumed, using `gfs_pio_write` or `gfs_pio_read`. Delete maps Gfarm errors to `errno` but does not fatal-error on unlink failure.

## State and Persistence
Gfarm stores persistent data. Runtime state is limited to global hints and per-file `GFS_File` wrappers. `Gfarm_sync` is a no-op because the code treats libgfarm as having no relevant client cache; per-file sync uses `gfs_pio_sync`.

## Dependencies and Integration Points
Requires `<gfarm/gfarm.h>`, undefines Gfarm package macros to avoid conflicts, and registers mdtest support. There are no backend-specific command-line options.

## Risks and Edge Cases
- Transfer loop calculates `sz` once, so if `len > 1 GiB`, subsequent iterations still request the original capped size even when `rem` becomes smaller.
- Access ignores requested mode and only checks existence via stat.
- Stat conversion fills uid/gid with local process ids rather than Gfarm metadata.
- Delete errors only set `errno`; callers relying on fatal delete failure may miss it.

## Test Signals
Exercise large transfers around the 1 GiB cap, dry-run paths, fsync, stat/statfs conversion, mkdir/rmdir/access, and error propagation for missing files.
