# File Research: sources/os/plan9/plan9/sys/src/cmd/vac/vac.h

Purpose: public Vac API and format constants shared by Vac tools.

Key contents:
- Forward declarations for `VacFs`, `VacDir`, `VacFile`, and `VacDirEnum`.
- Mode bit definitions for Unix/Plan 9 permissions plus append, exclusive, link, directory, DOS flags, snapshot, device, and named pipe.
- Metadata constants: `MetaMagic`, header/index sizes, `DirMagic`, and optional directory section tags.
- `VacDir` format containing file entry locations, generation numbers, size, qid, owner strings, timestamps, mode, Plan 9 qid info, and qidspace annotations.
- `VacFs` public structure with name, score, root, Venti connection, mode, block size, qid counter, and cache.
- Public functions for opening/creating/syncing Vac filesystems, walking/creating/removing/reading/writing files, reading/changing metadata, directory enumeration, score matching, and entry access.

Integration points:
- Consumed by `vac.c`, `unvac.c`, `vacfs.c`, `file.c`, `pack.c`, and helper tests.
- The incomplete pragmas hide `VacFile` and `VacDirEnum` internals from users.

Risks:
- `VacFs` is not fully opaque and callers such as `vac.c` directly access `fs->score` and `fs->bsize`.
- Mode constants are archive-format-visible and should not be renumbered.
