# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devfs-posix.c

Implements host POSIX filesystem access as Plan 9 device `#U/fs`.

Key behavior:
- Uses `base = "/"` and builds host paths from Plan 9 channel names.
- Supports attach, clone, walk, stat, open, create, close, read, write, remove, and wstat.
- Uses POSIX `stat`, `open`, `read`, `write`, `lseek`, `mkdir`, `chmod`, `chown`, `opendir`, `readdir`, `closedir`, `rmdir`, `remove`, and `rename`.
- Tracks per-channel host metadata and open state in `Ufsinfo`.
- Packs directory entries into Plan 9 `Dir` records with owner/group set to `"unknown"`.
- Computes synthetic qids from host device plus a simple path hash, with version from `st_mtime`.

Important interfaces:
- `fsqid` maps host stat/path data to Plan 9 qids.
- `fspath` creates cleaned host paths.
- `fsdirread` implements directory enumeration with offset discipline and one-entry carryover.

Notable risks:
- Uses fixed `MAXPATH` and `NAME_MAX` buffers with `strcpy`/`strcat`.
- Qid path hashing is weak and path-derived, not inode-derived.
- Directory seeking only supports offset reset to zero.
