# File Research: sources/os/bsd/openbsd-src/sbin/mount/Makefile

This Makefile builds the generic `mount` command, links against `libutil`, installs `mount.8`, and includes `<bsd.prog.mk>`.

Filesystem-specific mount helpers reuse code from this directory, especially `getmntopts.c` and `mntopts.h`.
