# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/dir.c

Implements ext2 directory scanning, validation, entry repair, orphan reconnection, and lost+found handling.

Directory traversal:
- `dirscan` walks directory blocks and applies the caller-provided `inodesc` callback to each entry.
- `fsck_readdir` validates and returns the next `ext2fs_direct` entry, salvaging corrupted directory blocks by creating empty records when allowed.
- `dircheck` enforces ext2 directory entry invariants: valid inode number, nonzero aligned record length, record fitting inside the block, valid name length, no embedded NUL or slash, and optional ext2 file-type rules.

Connectivity and repairs:
- `propagate` builds child/sibling links from cached directory inodes and marks directories reachable from root as `DFOUND`.
- `fileerror` and `direrror` print inode and pathname diagnostics.
- `adjust` corrects inode link counts or clears unreferenced objects.
- `makeentry`, `changeino`, `mkentry`, and `chgino` insert or modify directory entries.
- `expanddir` attempts to grow a directory by allocating a new block and splitting existing content.
- `allocdir` creates a new directory inode with `.` and `..`, initializes link counts, and updates parent accounting.
- `linkup` reconnects unreferenced files/directories into `lost+found`, creating or reallocating `lost+found` when necessary.
- `freedir` and `lftempname` support rollback and generated `#<ino>` names.

The implementation is ext2-aware: it handles little-endian fields, ext2 directory file-type feature bits, ext2 block size, ext2 root inode numbering, and ext2 inode mode/type conversion.
