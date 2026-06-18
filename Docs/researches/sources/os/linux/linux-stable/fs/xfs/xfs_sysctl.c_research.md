# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_sysctl.c

Registers and handles XFS sysctl knobs under `fs/xfs`.

Key elements:
- `xfs_table_header` stores the registered sysctl table handle.
- `xfs_stats_clear_proc_handler` wraps `proc_dointvec_minmax`; when a write sets the value nonzero, it clears global XFS stats and resets `xfs_stats_clear` to zero.
- `xfs_panic_mask_proc_handler` updates `xfs_panic_mask`; debug builds force shutdown-corrupt and log-reservation panic tags on.
- `xfs_deprecated_dointvec_minmax` emits a ratelimited deprecation warning on write before delegating to `proc_dointvec_minmax`.

Sysctl table entries:
- `panic_mask`
- `error_level`
- `xfssyncd_centisecs`
- `inherit_sync`
- `inherit_nodump`
- `inherit_noatime`
- `inherit_nosymlinks`
- `rotorstep`
- `inherit_nodefrag`
- `filestream_centisecs`
- `speculative_prealloc_lifetime`
- `stats_clear` when `CONFIG_PROC_FS` is enabled

Registration:
- `xfs_sysctl_register` registers the table at `fs/xfs`.
- `xfs_sysctl_unregister` unregisters the stored table header.

Important dependencies:
- Tunable storage is `xfs_params` from `xfs_sysctl.h`.
- Stats clearing depends on `xfs_stats_clearall` and global `xfsstats`.
- Panic mask semantics come from `xfs_error.h`.

Research notes:
- Each knob uses min/max validation through `xfs_params`.
- `stats_clear` is intentionally write-triggered and self-resetting.
