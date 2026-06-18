# File Research: sources/os/plan9/plan9/sys/src/cmd/ext2srv/ext2fs.c

Implements the lib9p `Srv` callbacks for the ext2 filesystem server. It is the 9P-facing layer over the lower-level ext2 code in `ext2subs.c`.

Key behavior:
- `rattach()` maps an attach `aname` to an `Xfs`, loads inode 2, and creates the root qid.
- `rclone()` copies `Xfile` state into a new fid.
- `rwalk1()` handles single-element walks, including `.`, `..`, root handling, and directory lookup through `get_file()`.
- `rstat()` and `rwstat()` convert between Plan 9 `Dir` structures and ext2 inode/directory metadata.
- `rread()` dispatches to `readdir()` or `readfile()`.
- `rwrite()` allows writes only to regular files.
- `ropen()` handles `OTRUNC` through `truncfile()`.
- `rcreate()` creates files or directories, then mutates the fid to refer to the new inode.
- `rremove()` delegates to ext2 `unlink()`.

Important implementation details:
- `response()` centralizes conversion from global `errno` to lib9p `respond()`.
- Walk errors restore `pinbr` so failed walks do not corrupt parent tracking.
- Directory permissions derive from the parent mode and requested Plan 9 permissions.

Risks and invariants:
- Uses a global `errno` defined in `xfssrv.c`, not C library `errno`.
- Commented permission checks indicate incomplete security enforcement for remove and related operations.
