# File Research: sources/os/plan9/9front/sys/src/cmd/dossrv/iotrack.h

## Purpose
Defines lock, sector-cache, and track-cache structures for `dossrv`.

## Key Contents
- Buffer flags: `BSTALE`, `BMOD`, and `BIMM`.
- `MLock` is a simple integer lock used by the server’s single-process/cooperative paths.
- `Iosect` stores next pointer, flags, lock, sector buffer pointer, and owning `Iotrack`.
- `Iotrack` stores hash/LRU links, lock, flags, refcount, owning `Xfs`, track address, and sector-wrapper table/data pointer.

## Notes
The cache treats a track as the I/O unit but exposes sector-sized locked views to FAT code.
