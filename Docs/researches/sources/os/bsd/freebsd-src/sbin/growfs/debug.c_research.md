# File Research: sources/os/bsd/freebsd-src/sbin/growfs/debug.c

`debug.c` is compiled only with `FS_DEBUG` and provides detailed dump routines for growfs internals.

Key behavior:
- Opens/closes a debug output file, with `-` mapped to `/dev/stdout`.
- Dumps full filesystem blocks as hex.
- Dumps UFS superblock fields, including legacy UFS1 fields, UFS2 fields, cylinder summary totals, snapshot inode list, flags, and geometry values.
- Dumps cylinder group fields and embedded cylinder summary.
- Dumps cylinder summaries and total cylinder summaries.
- Dumps inode allocation, fragment allocation, cluster allocation, and cluster summary maps.
- Contains disabled legacy code for rotational layout tables under `NOT_CURRENTLY`.
- Dumps UFS1 and UFS2 dinodes, including direct and indirect block pointers relevant to file size.
- Dumps indirect blocks with element width selected by filesystem type.

Important details:
- All functions return immediately if the debug log is not open.
- The file is diagnostic-only and has no effect in normal builds.
- Some formatting accesses wide fields via integer pointer casts, which is why the debug build disables cast-alignment warnings.
