# File Research: sources/os/plan9/plan9/sys/src/9/boot/bootcache.c

Optional boot-time cache filesystem wrapper.

Key behavior:
- `cache(fd)` checks for `/boot/cfs`; if missing, returns the original root fd.
- Reads `#e/cfs` options; `off` disables cache, an existing path selects cache partition.
- Otherwise derives a cache partition from `bootdisk` or default `bootdisk`.
- Starts `/boot/cfs` as `bootcfs`, optionally with `-r` when `fflag` is set, using a pipe to proxy the original fd through CFS.
- Returns the pipe fd to use as the root connection.

This is used when the boot image includes CFS support.
