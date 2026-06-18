# File Research: sources/teaching/minix/minix/fs/ext2/path.c

This file implements ext2 path component lookup and directory entry mutation.

Key entry points:
- `fs_lookup()`: looks up a name under a directory inode and returns fsdriver node metadata.
- `advance()`: resolves one directory component and opens the target inode.
- `search_dir()`: handles lookup, insertion, deletion, and directory-empty checks.

Directory logic:
- Validates directory inode type.
- Rejects names longer than `EXT2_NAME_MAX`.
- For `ENTER`, computes aligned required record size, reuses cached insertion hints, finds empty entries, shrinks existing entries, or extends the directory with `new_block()`.
- For `DELETE`, clears `d_ino`, optionally saves inode number inside the name field, marks parent dirty, resets `EXT2_INDEX_FL` when HTree is unsupported, and merges with previous entry.
- For `LOOK_UP`, returns the entry inode number.
- For `IS_EMPTY`, ignores `.` and `..`.

Feature interaction:
- When `INCOMPAT_FILETYPE` is present, `ENTER` writes ext2 directory file type values from inode mode.

Notable assumptions:
- Directories are assumed not to have holes.
- Directory record traversal trusts existing record lengths.
