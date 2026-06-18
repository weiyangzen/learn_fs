# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/request.c

This file implements the complete flashfs 9P request handler layer.

Key behavior:
- Attaches fids to the root entry and keeps per-fid `Entry`/directory-reader state.
- Enforces open permissions, read-only mode, and directory write restrictions.
- Handles create, remove, chmod-like wstat, truncating open, reads, writes, stats, walks, and fid destruction.
- Reads regular files through `eread`.
- Writes regular files by splitting data into journal-sized chunks, allocating extents, appending `FT_WRITE` records, and updating the entry tree.
- Logs create, trunc, remove, and chmod operations into the flash journal.

Important details:
- Uses `need()` before writing journal records to trigger compaction or fail when full.
- Rejects names longer than `MAXNSIZE`.
- OTRUNC is journaled as `FT_trunc` and assigns a new file number.
- Partial walks clear errors when at least one element succeeds, matching Plan 9 walk semantics.
- Mounts service name `brzr`.

Filesystem relevance:
- Direct: production flashfs user-facing 9P server operations.
