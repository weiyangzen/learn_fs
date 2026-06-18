# File Research: sources/os/plan9/9front/sys/src/cmd/dossrv/dat.h

## Purpose
Central data-structure and constant header for the FAT-backed `dossrv` 9P server.

## Key Contents
- Defines DOS partition type constants for FAT12/FAT16/FAT32 variants and related values.
- Defines on-disk structures: `Dospart`, FAT boot sectors (`Dosboot`, `Dosboot32`), optional `Fatinfo`, and `Dosdir`.
- Defines `Dosbpb`, the in-memory BIOS parameter block and FAT state, including cluster geometry, FAT location, root/data addresses, FAT width, free-cluster tracking, and lock.
- Defines FAT directory constants, attributes, endian access macros, and file-size/name limits.
- `Dosptr` tracks the current directory entry location, parent location, cluster cache, previous/next directory sectors, and held `Iosect`.
- `Xfs` tracks an attached FAT filesystem/device with file name, qids, refcount, sector geometry, byte offset, open mode, and `Dosbpb`.
- `Xfile` tracks a 9P fid, open flags, qid, attached filesystem, and current DOS pointer.
- Enumerates xfile cleanup modes, filename classification results, xfile open flags, and internal errno codes.

## Interfaces And Dependencies
- Assumes `MLock` and `Iosect` are already declared from `iotrack.h`.
- Exposes global declarations for `chatty`, `errno`, `readonly`, `deffile`, and `trspaces`.

## Notes
This header is the integration point for disk format parsing, sector cache state, and 9P fid state. Many modules depend on its exact struct fields.
