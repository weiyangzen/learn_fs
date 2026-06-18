# File Research: sources/os/linux/linux-stable/fs/befs/super.h

This header declares BeFS superblock load and validation helpers.

Exports:
- `befs_load_sb()`
- `befs_check_sb()`

Integration:
- Implemented in `super.c`.
- Used by `linuxvfs.c` during mount.

Risk notes:
- No include guard, but the header is tiny and narrowly included.
