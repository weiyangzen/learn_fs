# File Research: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_lookup.c

Implements ext2 directory reading, name lookup, directory entry mutation, emptiness checks, and rename path validation.

Key entry points:
- `ext2fs_readdir()` reads ext2 directory blocks and converts entries to BSD `struct dirent`.
- `ext2fs_lookup()` performs namecache lookup, linear directory scanning, create/delete/rename setup, and vnode locking rules.
- `ext2fs_search_dirblock()` scans one directory block, validates forward progress, finds matches, and records reusable slots.
- `ext2fs_direnter()` inserts a new entry, either by appending a fresh block or compacting free space.
- `ext2fs_dirremove()` removes an entry by zeroing the first entry in a block or merging with the previous record.
- `ext2fs_dirrewrite()` retargets an existing entry.
- `ext2fs_dirempty()` accepts only `.` and matching `..`.
- `ext2fs_checkpath()` prevents directory renames that would create cycles.

Important behavior:
- Directory record lengths are ext2 lengths, while exported `dirent` lengths are recomputed for BSD ABI.
- Lookup stores mutation state in the directory inode: `i_offset`, `i_count`, `i_reclen`, `i_ino`, and `i_endoff`.
- Creation searches for reusable slots and supports compaction when enough fragmented free space exists.
- Delete and rename paths enforce directory write permission, sticky-directory ownership rules, and read-only mount restrictions.
- `..` lookup unlocks the parent before fetching the target to avoid vnode lock deadlocks.

Dependencies:
- Uses `ext2fs_bufatoff()`, `ext2fs_truncate()`, `ext2fs_setsize()`, `VFS_VGET()`, namecache APIs, and UFS `ufs_dirbad()` diagnostics.
- Directory file type fields are filled only when ext2 revision/features support `EXT2F_INCOMPAT_FTYPE`.

Watch points:
- Full directory entry validation is gated by `dirchk`; malformed entries normally only require nonzero record length for progress.
- `ext2fs_dirbadentry()` prints and panics when enabled, so it is diagnostic rather than recoverable validation.
- `ext2fs_readdir()` converts one entry at a time and has an explicit TODO to batch conversions.
