# File Research: sources/os/linux/linux/fs/jfs/jfs_debug.c

## Purpose
Creates and removes `/proc/fs/jfs` debug/statistics entries when procfs plus JFS debug or statistics support is enabled.

## Key Functions
- `jfs_loglevel_proc_show()` prints current `jfsloglevel`.
- `jfs_loglevel_proc_open()` wraps the show function with `single_open()`.
- `jfs_loglevel_proc_write()` reads one user byte, accepts ASCII digits only, and sets `jfsloglevel`.
- `jfs_proc_init()` creates `/proc/fs/jfs`, optional stats entries (`lmstats`, `txstats`, `xtstat`, `mpstat`), optional debug entries (`TxAnchor`, `loglevel`).
- `jfs_proc_clean()` removes the proc subtree.

## Compile-Time Behavior
- Entire body is under `PROC_FS_JFS`.
- Loglevel handling and `TxAnchor` are under `CONFIG_JFS_DEBUG`.
- Statistics entries are under `CONFIG_JFS_STATISTICS`.

## Dependencies
- Uses procfs and seq_file APIs.
- Function declarations and `PROC_FS_JFS` are controlled by `jfs_debug.h`.
