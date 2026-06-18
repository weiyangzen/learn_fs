# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_debug.c

Creates optional JFS procfs debug/statistics entries.

Behavior:
- Compiled only when `PROC_FS_JFS` is defined by debug/statistics config plus procfs.
- Under `CONFIG_JFS_DEBUG`, exposes `/proc/fs/jfs/loglevel` with seq read and single-character write to update `jfsloglevel`.
- `jfs_proc_init()` creates `/proc/fs/jfs` and optional statistics/debug files: `lmstats`, `txstats`, `xtstat`, `mpstat`, `TxAnchor`, and `loglevel`.
- `jfs_proc_clean()` removes the proc subtree.

Risk notes:
- Loglevel write accepts only one ASCII digit and does not parse multi-digit input.
