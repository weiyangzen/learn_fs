# File Research: sources/local-fs/ocfs2-tools/fswreck/special.c

This file handles root/lost+found style special corruptions.

Key behavior:
- `mess_up_root()` ignores the passed block number, resolves the filesystem root block from the superblock, reads the root inode, verifies it is valid, sets `i_mode` to zero, and writes it back.
- This makes the root no longer a directory, which also makes normal lost+found lookup fail.

Integration notes:
- Used for `ROOT_NOTDIR`, `ROOT_DIR_MISSING`, and `LOSTFOUND_MISSING` codes through `corrupt_file()`.
- The printed message always labels the corruption as `ROOT_NOTDIR` even when invoked for related codes.
