# File Research: sources/os/linux/linux-stable/fs/cramfs/internal.h

This header declares the CramFs zlib wrapper interface.

Key responsibilities:
- Declares `cramfs_uncompress_block()`.
- Declares `cramfs_uncompress_init()`.
- Declares `cramfs_uncompress_exit()`.

Dependencies:
- Implemented by `uncompress.c`.
- Used by `inode.c`.

Risks and invariants:
- The interface exposes a module-global decompression stream lifecycle.
