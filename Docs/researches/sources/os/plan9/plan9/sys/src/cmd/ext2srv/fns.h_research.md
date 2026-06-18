# File Research: sources/os/plan9/plan9/sys/src/cmd/ext2srv/fns.h

Declares the cross-file API for `ext2srv`.

Key contents:
- Logging, panic, error conversion, and UID/GID map loading.
- `Xfs` and `Xfile` lifecycle helpers.
- 9P-facing ext2 operations such as inode lookup, file lookup, stat conversion, read/write/readdir, create, unlink, truncate, and wstat.
- Allocation and bitmap helpers for ext2 blocks and inodes.
- Buffer cache operations from `iobuf.c`.

Important relationships:
- Bridges the lib9p callbacks in `ext2fs.c` with the ext2 implementation in `ext2subs.c`.
- Includes legacy or unused declarations such as FAT-oriented names, indicating shared ancestry with other filesystem servers.

Risks and invariants:
- Function prototypes use old-style spacing and shared globals, matching the Plan 9 codebase style.
- Maintaining this header requires keeping it synchronized with multiple implementation files because there are no module-level private headers.
