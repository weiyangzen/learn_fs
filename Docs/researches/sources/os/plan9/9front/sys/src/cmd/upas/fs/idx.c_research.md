# File Research: sources/os/plan9/9front/sys/src/cmd/upas/fs/idx.c

This file reads and writes `.idx` cache files for `upas/fs`.

Key behavior:
- Maintains interned strings for repeated MIME/type values.
- `wridxfile` writes a temporary exclusive index, prints magic/version/backend header, serializes all messages recursively, then renames to `<mailbox>.idx`.
- `pridxmsg` serializes digest, flags, fileid, lines, header fields, MIME metadata, sizes, bad-char count, backend aux, and child count.
- `rdidxfile` opens and validates index magic/backend metadata, compares qids, marks existing messages, and merges index entries into live message trees.
- `rdidx` handles recursive child messages, validates digest/fileid/size invariants, restores flags and cached metadata, and detects stale/dead entries.
- `genericidxread/write/invalid` provide default backend index metadata behavior.

Integration and risks:
- Uses digest AVL tree (`mtree`) to merge top-level indexed entries with live mailbox scans.
- Index writes can overwrite mutable information from concurrent upas/fs instances; comments call out this limitation.
- Exclusive open/rename behavior is Plan 9 specific and mirrored by test helpers.
