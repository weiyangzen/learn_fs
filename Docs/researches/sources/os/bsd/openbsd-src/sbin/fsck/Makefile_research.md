# File Research: sources/os/bsd/openbsd-src/sbin/fsck/Makefile

Builds the generic `fsck` dispatcher program from `fsck.c`, `fsutil.c`, and `preen.c`.

Notable build settings:
- Installs `fsck.8`.
- Links against `libutil`.
- Uses the standard OpenBSD `bsd.prog.mk` program build rules.
