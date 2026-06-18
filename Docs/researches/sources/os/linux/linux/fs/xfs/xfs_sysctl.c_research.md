# File Research: sources/os/linux/linux/fs/xfs/xfs_sysctl.c

## Purpose

`xfs_sysctl.c` registers XFS tunables under the kernel sysctl tree `fs/xfs`. It exposes error behavior, inode flag inheritance defaults, legacy timers, allocation behavior, filestream timeout, speculative preallocation cleanup lifetime, and stats clearing.

## Main Interfaces

- `xfs_sysctl_register()`: registers `xfs_table` at `fs/xfs`.
- `xfs_sysctl_unregister()`: unregisters the table.
- `xfs_stats_clear_proc_handler`: write handler for `stats_clear` when procfs support is enabled.
- `xfs_panic_mask_proc_handler`: write handler for `panic_mask`, adding mandatory debug panic bits in debug builds.
- `xfs_deprecated_dointvec_minmax`: helper that warns on writes to deprecated sysctl options. It is defined in this file but not used by the current table.

## Tunables

- `panic_mask`: controls panic behavior for selected XFS error tags.
- `error_level`: controls how much corruption/error detail XFS reports.
- `xfssyncd_centisecs`: legacy sync daemon timer parameter.
- `inherit_sync`, `inherit_nodump`, `inherit_noatime`, `inherit_nosymlinks`, `inherit_nodefrag`: default inheritance behavior for inode flags.
- `rotorstep`: inode32 allocation group rotation control.
- `filestream_centisecs`: filestream directory-to-AG association timeout.
- `speculative_prealloc_lifetime`: blockgc/speculative preallocation lifetime.
- `stats_clear`: procfs-enabled write-only behavior to clear global stats.

## Implementation Notes

- Most entries use `proc_dointvec_minmax` with min/max values from `xfs_params`.
- `stats_clear` calls `xfs_stats_clearall(xfsstats.xs_stats)` when written with a nonzero value, then resets the stored sysctl value to zero.
- `panic_mask` mirrors the sysctl value to the global `xfs_panic_mask`; debug builds force corruption-shutdown and log-reservation panic bits.
- The table is static const and registration stores its header in `xfs_table_header`.

## Dependencies and Callers

- Includes `xfs_platform.h` and `xfs_error.h`.
- Uses `xfs_params`, `xfs_panic_mask`, `xfs_stats_clear`, and global `xfsstats`.
- Called by `init_xfs_fs` and `exit_xfs_fs` in `xfs_super.c`.

## Research Notes

- Sysctl support is optional at the header level; this implementation is compiled when the build includes the relevant source.
- The sysctl ABI overlaps conceptually with sysfs stats clearing, but sysctl clearing targets global stats only.
