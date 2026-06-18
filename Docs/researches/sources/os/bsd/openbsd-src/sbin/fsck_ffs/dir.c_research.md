# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ffs/dir.c

Implements FFS/UFS directory scanning, validation, insertion, expansion, lost+found handling, and directory connectivity propagation.

Directory scanning:
- `dirscan` walks UFS directory entries in filesystem blocks/fragments and applies an `inodesc` callback.
- `fsck_readdir` returns the next valid `struct direct` or repairs a corrupted directory block into an empty record when allowed.
- `dircheck` validates inode range, record length, alignment, record fit, name length, file type range, no embedded NUL/slash, and required terminating NUL.

Repair behavior:
- `propagate` marks a connected directory subtree with the state of a starting inode.
- `fileerror`/`direrror` print path and inode diagnostics.
- `adjust` fixes link counts or clears unreferenced objects.
- `makeentry` and `changeino` add or rewrite directory entries.
- `expanddir` allocates a new directory block, moves existing content, fills empty directory blocks, and rolls back on failure.
- `allocdir` creates a new directory with `.` and `..`, initializes link counts, caches it, inherits parent uid/gid, and updates parent counts.
- `linkup` reconnects orphan files/directories to `lost+found`, creates/reallocates `lost+found` if needed, updates `..`, and adjusts link-count accounting.
- `freedir`, `lftempname`, and `getdirblk` support rollback, generated orphan names, and held directory-block access.

Compared with ext2’s directory code, this version uses UFS `struct direct`, `DIRBLKSIZ`, fragment-aware directory sizing, UFS inode state macros, and FFS allocation helpers.
