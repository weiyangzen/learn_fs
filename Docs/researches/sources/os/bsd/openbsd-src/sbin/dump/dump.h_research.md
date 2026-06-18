# File Research: sources/os/bsd/openbsd-src/sbin/dump/dump.h

## Purpose
Central shared header for the UFS `dump` program.

## Key Contents
- Declares inode state maps: `usedinomap`, `dumpdirmap`, `dumpinomap`, plus `SETINO`, `CLRINO`, and `TSTINO`.
- Declares global dump configuration and runtime state: disk/tape paths, dump level, file descriptors, tape geometry, remote host, transfer stats, superblock, output blocking, DUID, and flags.
- Declares operator interface functions, mapping functions, dumping functions, tape writing functions, remote dump functions, and utility functions.
- Defines dump exit codes:
  - `X_FINOK`
  - `X_STARTUP`
  - `X_REWRITE`
  - `X_ABORT`
- Defines dumpdates structures and iteration macro `ITITERATE`.

## Notes
This header exposes most of the program as shared global state, reflecting the historical multi-file design.
