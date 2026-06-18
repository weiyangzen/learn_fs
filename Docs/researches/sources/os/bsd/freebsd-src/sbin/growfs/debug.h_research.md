# File Research: sources/os/bsd/freebsd-src/sbin/growfs/debug.h

`debug.h` defines the growfs debug API and turns it into no-op macros when `FS_DEBUG` is not set.

Key contents:
- Under `FS_DEBUG`, declares dump functions for superblocks, cylinder groups, cylinder summaries, inode maps, fragment maps, cluster maps, inodes, indirect blocks, and hex blocks.
- Defines debug levels `DL_TRC` and `DL_INFO` and external `_dbg_lvl_`.
- Provides tracing macros for function entry/exit, trace points, and formatted debug printing.
- Selects UFS1 or UFS2 inode dump based on `fs_magic`.
- Without `FS_DEBUG`, all debug macros expand to nothing.

This header lets `growfs.c` contain extensive instrumentation with zero normal-build runtime behavior.
