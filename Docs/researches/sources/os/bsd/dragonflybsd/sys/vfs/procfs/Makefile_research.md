# File Research: sources/os/bsd/dragonflybsd/sys/vfs/procfs/Makefile

This Makefile builds the `procfs` kernel module from the process-control, map, note, rlimit, status, subr, type, VFS, and vnode operation files.

Notably, architecture-sensitive register files (`procfs_regs.c`, `procfs_fpregs.c`, `procfs_dbregs.c`) are not listed here, implying they may be pulled in elsewhere or excluded by this module definition.

Research notes: module composition centers on pseudo-files under `/proc`, with most dispatch in `procfs_vnops.c` and read/write routing in `procfs_subr.c`.
