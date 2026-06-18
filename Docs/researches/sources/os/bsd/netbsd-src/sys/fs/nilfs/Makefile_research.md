# File Research: sources/os/bsd/netbsd-src/sys/fs/nilfs/Makefile

This kernel include makefile installs NILFS public headers under `/usr/include/fs/nilfs`. It exports `nilfs_mount.h` and `nilfs_fs.h` through NetBSD's `bsd.kinc.mk` include-install machinery.

Integration points: userland and kernel consumers that need NILFS mount arguments or on-disk structure definitions depend on this installed header set. Internal implementation header `nilfs.h` and endian helper `nilfs_bswap.h` are not installed here.

Risk is mainly export drift: if mount ABI or on-disk declarations move to another header, this file must be kept aligned with what userland tools need.
