# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_kernel.h

## Purpose

`lfs_kernel.h` provides kernel-only LFS support declarations and compatibility fcntl definitions that do not belong in the on-disk/userland `lfs.h` interface.

## Main Contents

- Declares global `struct lfs_stats lfs_stats`.
- Defines `LFS_SEGLOCK_HELD(fs)` as a wrapper around `lfs_seglock_held(fs)`.
- Defines `struct lfs_cluster`, the async clustered write descriptor used by `lfs_writeseg()` and `lfs_cluster_work()`. It stores copied-buffer size, buffer pointer array, buffer count, flags, owning filesystem, and synchronous segment pointer.
- Defines cluster flags `LFS_CL_MALLOC`, `LFS_CL_SHIFT`, and `LFS_CL_SYNC`.
- Defines `struct lbnentry`, the splay-tree node used to track logical block numbers allocated through `lfs_balloc`.
- Defines legacy/compat LFS fcntl command numbers for old `timeval50`, old `BLOCK_INFO_70`, ifile handle, reclaim, and log-wrap controls.

## Integration Notes

This header is included by the kernel LFS implementation files that need segment-lock checks, clustered write state, private logical-block tracking, or compat fcntl command definitions. Userland tools are expected to use the current public LFS command definitions instead of these compat forms.
