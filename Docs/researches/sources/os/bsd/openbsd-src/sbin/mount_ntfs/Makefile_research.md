# File Research: sources/os/bsd/openbsd-src/sbin/mount_ntfs/Makefile

This Makefile builds `mount_ntfs` only on `alpha`, `amd64`, and `i386`; other architectures set `NOPROG`. It uses `mount_ntfs.c` plus shared `getmntopts.c`, installs `mount_ntfs.8`, and includes the generic mount directory.

The architecture gate reflects NTFS helper/kernel support constraints.
