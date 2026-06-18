# File Research: sources/os/linux/linux-stable/fs/jffs2/symlink.c

This file defines JFFS2 inode operations for symbolic links.

Key responsibilities:
- Uses `simple_get_link` for symlink target lookup.
- Reuses `jffs2_setattr` for attribute changes.
- Reuses `jffs2_listxattr` for xattr listing.

Important interactions:
- Symlink target storage and caching are handled elsewhere, especially `readinode.c` for target read/caching and write/create paths for raw inode data.

Notable invariants and risks:
- The file is intentionally minimal; correctness depends on `f->target` being populated before VFS link resolution uses `simple_get_link`.
