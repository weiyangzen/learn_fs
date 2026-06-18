# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_debug.c

Read completely: 331 lines.

Provides DEBUG-only LFS logging, dumping, and consistency-check helpers. With `DEBUG` undefined, the file contributes no runtime code beyond the RCS metadata guard.

Debug facilities:
- Defines a circular `lfs_log` array and `lfs_lognum`.
- `lfs_bwrite_log()` records non-gathered/non-delayed writes before calling `VOP_BWRITE()`.
- `lfs_dumplog()` prints the circular write log with block number, operation, flags, pid, line, and basename.
- `lfs_dump_super()` prints selected superblock geometry, checkpoint, mask/shift, checksum, maxfilesize, and superblock-location fields through accessors.
- `lfs_dump_dinode()` prints inode metadata and direct/indirect block addresses.
- `lfs_check_bpp()` verifies that buffers in a segment buffer array map to contiguous physical disk addresses and reports mismatches.
- `lfs_debug_log()` routes enabled subsystem debug messages to `vlog(LOG_DEBUG, ...)`.

Disabled or weak checks:
- `lfs_check_segsum()` currently returns immediately, so its later segment-summary bounds/overwrite checks are effectively disabled.
- Some diagnostic paths retain DDB hooks and `panic()` calls but are unreachable because of the early return.

Risks and notes:
- This file is diagnostic-only and compiled under `DEBUG`, but its `lfs_bwrite_log()` wrapper changes write logging paths when enabled.
- Debug subsystem enabling is controlled by the `lfs_debug_log_subsys[]` array.
