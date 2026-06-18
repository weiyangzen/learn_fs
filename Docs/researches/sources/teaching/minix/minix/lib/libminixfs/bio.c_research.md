# File Research: sources/teaching/minix/minix/lib/libminixfs/bio.c

This file adapts `libminixfs` cache primitives to libfsdriver block I/O hooks for filesystems that may serve root filesystem block-device access.

Key exported functions:
- `lmfs_driver(dev, label)`: thin wrapper over `bdev_driver` to associate a device major with a driver label.
- `lmfs_bio(dev, data, bytes, pos, call)`: common implementation for block read, write, and peek.
- `lmfs_bflush(dev)`: flushes and invalidates all cached blocks for a device.

`lmfs_bio` behavior:
- Validates device, offset, length, and overflow.
- Queries partition geometry using `DIOCGETP` on every call to honor repartitioning.
- Clips transfers at partition EOF.
- Splits byte ranges into filesystem-block-aligned cache blocks.
- Uses `block_prefetch` before reads/peeks to build larger block-driver requests.
- Avoids disk reads for full-block writes by using `NO_READ`.
- Uses `lmfs_get_partial_block` for the final partial device block.
- Copies to/from user buffers through `fsdriver_copyin` and `fsdriver_copyout`.
- Marks written buffers dirty even if copyin failed, because the copy may have partially succeeded.
- Returns transferred byte count if any progress was made; otherwise returns the underlying error.

Important interactions:
- Uses `lmfs_fs_block_size`, `lmfs_get_block`, `lmfs_get_partial_block`, `lmfs_put_block`, `lmfs_markdirty`, `lmfs_readahead`, `lmfs_flushdev`, and `lmfs_invalidate`.
- Uses `bdev_ioctl` for geometry and cache-level helpers for actual data access.

Operational notes:
- Writes complete into cache, not necessarily onto disk immediately.
- `lmfs_bflush` first flushes dirty blocks, then purges local and VM cache state.
