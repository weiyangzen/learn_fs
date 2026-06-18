# File Research: sources/os/plan9/plan9/sys/src/cmd/vac/dat.h

Internal data definitions for the Vac filesystem/archive implementation.

Defines:
- `MetaBlock` and `MetaEntry` forward declarations.
- `MaxBlock` limit.
- Tuning constants for estimated directory-entry size, fullness threshold, flush size, and dirty percentage.
- `MetaEntry`, a pointer plus size wrapper for one metadata entry.
- `MetaBlock`, tracking metadata block size, used/free space, index allocation/use, unbotch flag, and buffer pointer.
- `VacDirEnum`, directory enumeration state containing `VacFile`, block offset, entry indexes, and buffered `VacDir` entries.

This header supports metadata packing and directory enumeration in the broader `vac` codebase.
