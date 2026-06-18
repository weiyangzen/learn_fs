# File Research: sources/local-fs/jfsutils/libfs/super.h

This header declares the shared superblock/logsuper helpers from `super.c`:

- `ujfs_validate_logsuper()`
- `ujfs_validate_super()`
- `ujfs_put_superblk()`
- `ujfs_get_superblk()`
- `ujfs_put_logsuper()`
- `ujfs_get_logsuper()`
- `inrange()`

It forward-declares `struct superblock` and `struct logsuper`, includes `utilsubs.h` for common types/includes, and uses guard `H_SUPER`.
