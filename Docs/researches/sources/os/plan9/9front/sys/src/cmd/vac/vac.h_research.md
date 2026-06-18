# File Research: sources/os/plan9/9front/sys/src/cmd/vac/vac.h

Purpose: Public Vac data model and API declarations.

Key behavior:
- Declares opaque `VacFile` and `VacDirEnum`, plus public `VacFs` and `VacDir`.
- Defines Vac mode bits for Unix/Plan 9 permissions, append, exclusive, link, directory, MS-DOS flags, snapshot, device, and named pipe.
- Defines metadata format constants and optional directory-entry tags.
- `VacDir` stores file name, Venti entry references, size, qid, uid/gid/mid, times, mode, Plan 9 qid metadata, and qid-space annotations.
- `VacFs` stores root score, root file, Venti connection, cache, block size, mode, and qid counter.
- Declares filesystem, file, directory enumeration, metadata, filter, and helper APIs used by `vac`, `unvac`, and `vacfs`.

Dependencies:
- Relies on Venti types such as `VtConn`, `VtCache`, `VtEntry`, `VtScoreSize`, and `Reprog`.

Notable details:
- `ModeDir` duplicates directory-entry state so Vac metadata can carry directory identity independently.
