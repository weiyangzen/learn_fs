# File Research: sources/os/bsd/openbsd-src/sbin/mount_cd9660/Makefile

This Makefile builds `mount_cd9660` from `mount_cd9660.c` plus shared `getmntopts.c`, installs `mount_cd9660.8`, adds the generic `mount` directory to include paths, and uses `.PATH` to find shared source.

It follows the common pattern for filesystem-specific mount helpers.
