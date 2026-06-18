# File Research: sources/os/bsd/openbsd-src/sbin/mknod/Makefile

This Makefile builds `mknod`, installs both `mknod.8` and `mkfifo.1`, and creates a hard link from `mknod` to `mkfifo`.

The shared binary changes behavior based on `__progname`.
