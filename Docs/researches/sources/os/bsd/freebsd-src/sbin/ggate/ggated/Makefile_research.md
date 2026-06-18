# File Research: sources/os/bsd/freebsd-src/sbin/ggate/ggated/Makefile

Builds the `ggated` daemon.

Key contents:
- Adds `.PATH` for the shared ggate sources.
- Builds `ggated` from `ggated.c` and shared `ggate.c`.
- Installs man page `ggated.8`.
- Assigns package `ggate`.
- Links `pthread` and `util`.
- Adds include path for `../shared`.

This target does not define `LIBGEOM`, so the shared `g_gate_list()` implementation is excluded for this daemon.
