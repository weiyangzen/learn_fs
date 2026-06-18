# File Research: sources/os/linux/linux/fs/jfs/jfs_debug.h

## Purpose
Defines JFS assertion, logging, procfs, and statistics macros.

## Main Definitions
- `PROC_FS_JFS` is enabled only when `CONFIG_PROC_FS` and either `CONFIG_JFS_DEBUG` or `CONFIG_JFS_STATISTICS` are set.
- `assert(p)` prints a critical BUG message and calls `BUG()` on failure.
- With `CONFIG_JFS_DEBUG`, `ASSERT()` maps to `assert()`, `jfsloglevel` is extern, and `jfs_info/debug/warn/err()` emit printk messages according to runtime loglevel.
- Without `CONFIG_JFS_DEBUG`, `ASSERT()` and logging macros compile to no-ops.
- With `CONFIG_JFS_STATISTICS`, proc show functions are declared and `INCREMENT`, `DECREMENT`, `HIGHWATERMARK` mutate counters.
- Without statistics, those counter macros are no-ops.

## Dependencies
- Debug proc show declarations use `struct seq_file`.
- Used broadly by JFS files for diagnostics and optional assertions.
