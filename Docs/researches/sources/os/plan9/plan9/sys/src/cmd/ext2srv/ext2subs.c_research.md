# File Research: sources/os/plan9/plan9/sys/src/cmd/ext2srv/ext2subs.c

Contains the main ext2 implementation for `ext2srv`: superblock handling, inode and block mapping, directory operations, file I/O, allocation, deletion, truncation, and bit operations.

Key behavior:
- Loads optional UID/GID maps from passwd/group-like files and maps numeric ext2 ids to Plan 9 names.
- `ext2fs()` validates the superblock, rejects unclean filesystems, computes layout parameters, and marks the filesystem not clean while mounted unless read-only.
- `CleanSuper()` marks the filesystem valid again when the last `Xfs` reference is dropped.
- `get_inode()`, `get_file()`, and `getname()` locate inodes and names using inode table and directory entries.
- `dostat()` and `dowstat()` translate stat and rename/mode/mtime updates.
- `readfile()` and `writefile()` perform block-level file I/O, including fast symlink reads.
- `readdir()` emits Plan 9 directory entries through `convD2M()`.
- `bmap()` resolves direct, indirect, double-indirect, and triple-indirect blocks.
- `getblk()`, `inode_getblk()`, and `block_getblk()` allocate blocks on write.
- `new_block()` and `new_inode()` update ext2 bitmaps, group counts, and superblock counts.
- `create_file()`, `create_dir()`, `add_entry()`, `unlink()`, `delete_entry()`, and `empty_dir()` maintain directory contents and link counts.
- `free_block_inode()`, `free_block()`, `free_inode()`, and `truncfile()` reclaim ext2 resources.

Important implementation details:
- Allocation strategy is derived from Linux ext2 code and attempts locality near goal blocks or parent inode group.
- Directory operations only iterate direct directory blocks up to `EXT2_NDIR_BLOCKS`.
- The server updates inode times and marks cached blocks dirty through `dirtybuf()`.

Risks and invariants:
- The code assumes classic ext2 layout and does not include journaling or modern ext4 feature negotiation.
- Several corruption checks set `Ecorrupt`, but recovery is limited.
- `new_inode()` contains a suspicious comparison where the same field is compared to itself when selecting a directory group, which may reduce allocation quality.
