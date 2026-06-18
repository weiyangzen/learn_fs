# File Research: sources/os/bsd/freebsd-src/sbin/dump/Makefile

## Purpose
Build definition for the UFS `dump` and `rdump` utilities.

## Main Elements
- Sets package to `ufs`.
- Builds `dump`, links `rdump` to it, and defines `RDUMP`.
- Installs `/dev/null` as `dumpdates` config target with group `operator` and mode `664`.
- Source list includes `itime.c`, `main.c`, `optr.c`, `dumprmt.c`, `tape.c`, `traverse.c`, `unctime.c`, and `cache.c`.
- Links `libufs`.
- Installs `dump.8` and `rdump.8` manpage link.
- Sets `WARNS?=2` and includes `bsd.prog.mk`.

## Dependencies And Integration
Part of FreeBSD UFS tooling. Build comments summarize major source roles and debug macros.

## Risk Notes
The installed `dumpdates` path and permissions are part of operational behavior; changes can affect dump scheduling metadata updates.
