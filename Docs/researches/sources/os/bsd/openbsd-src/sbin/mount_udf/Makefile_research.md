# File Research: sources/os/bsd/openbsd-src/sbin/mount_udf/Makefile

This Makefile builds `mount_udf` from `mount_udf.c` plus shared `getmntopts.c`, installs `mount_udf.8`, and imports the generic mount include/source path.

It follows the standard helper pattern for filesystem-specific `mount_*` commands.
