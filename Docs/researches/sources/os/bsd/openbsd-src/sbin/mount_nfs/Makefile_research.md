# File Research: sources/os/bsd/openbsd-src/sbin/mount_nfs/Makefile

This Makefile builds `mount_nfs` from `mount_nfs.c` plus shared `getmntopts.c`, installs `mount_nfs.8`, defines `NFS`, includes the generic mount directory, and uses `.PATH` for shared source.

It is the build wrapper for the RPC/NFS mount helper.
