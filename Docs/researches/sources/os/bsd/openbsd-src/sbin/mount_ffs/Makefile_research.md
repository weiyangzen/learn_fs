# File Research: sources/os/bsd/openbsd-src/sbin/mount_ffs/Makefile

This Makefile builds `mount_ffs` from `mount_ffs.c` plus shared `getmntopts.c`, installs `mount_ffs.8`, and includes the generic mount directory.

It provides the FFS-specific helper used by the generic `mount` command.
