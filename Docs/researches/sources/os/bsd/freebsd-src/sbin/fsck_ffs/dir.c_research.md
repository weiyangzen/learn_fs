# File Research: sources/os/bsd/freebsd-src/sbin/fsck_ffs/dir.c

This file contains directory-tree repair machinery: directory entry scanning, validation, link-count adjustment, lost+found reconnection, directory allocation, and directory expansion.

Key behavior:
- `propagate()` marks directories reachable from root as `DFOUND`.
- `check_dirdepth()` verifies and repairs UFS directory depth metadata, either by directly editing inodes or by background-fsck sysctl adjustment.
- `dirscan()` walks directory entries for a directory inode and applies an `inodesc` callback.
- `fsck_readdir()` validates current and next entries, can zero corrupt directory-block remainder, and can coalesce a bad following entry into the current record.
- `dircheck()` validates `d_reclen`, `d_namlen`, type range, name termination, slash/NUL rules, and optionally clears unused directory padding with `-z`.
- `adjust()` fixes inode link counts, clears soft-update orphan files, or reconnects unreferenced objects.
- `linkup()` reconnects orphan files/directories into `lost+found`, creating or reallocating `lost+found` when necessary.
- `changeino()` and `makeentry()` mutate or create directory entries.
- `expanddir()` allocates more directory space, including direct or single-indirect growth, and initializes empty directory records.
- `allocdir()` creates a directory inode with `.` and `..`, updates parent link counts, caches inode info, and records directory depth.
- `freedirino()` and `freeino()` unwind failed directory creation.
- `lftempname()` generates lost+found names like `#<ino>`.

Important interactions:
- Relies heavily on `ckinode()` from `inode.c` for walking directory blocks.
- Uses `inoinfo()` / `getinoinfo()` state from pass 1.
- Uses `sysctl` operations in background mode for live filesystem updates.
- Calls `allocino()`, `allocblk()`, `freeblock()`, `ginode()`, `inodirty()`, and `cgdirty()` for persistent metadata repair.

Edge cases:
- Directories with wrong depth can be silently left unresolved in no-write/read-only mode because clean state does not depend on depth.
- Orphans inside snapshots cannot be linked up.
- Directory expansion is deliberately limited to direct blocks plus one single-indirect block.
- Broken `lost+found` can be replaced, with old inode reference accounting repaired.
