# File Research: sources/os/linux/linux/fs/efs/dir.c

Implements EFS directory iteration.

Key behavior:
- Exposes directory file operations with generic llseek/read, `efs_readdir`, and generic lease support.
- Directory inode operations only provide lookup.
- `efs_readdir()` maps `ctx->pos` to an EFS directory block and slot.
- Reads each directory block through `sb_bread(efs_bmap())`.
- Validates the EFS directory block magic.
- Iterates active slots, validates name bounds, and emits directory entries with inode numbers and unknown d_type.
- Updates `ctx->pos` using block/slot encoding.

Important interactions:
- Uses EFS fixed 512-byte directory blocks and slot offset tables.
- Relies on `efs_bmap()` for logical-to-physical block mapping.
