# File Research: sources/os/linux/linux/fs/ntfs/bdev-io.c

Provides direct block-device I/O helpers for NTFS metadata reads and block-device page-cache writes.

Key entry points:
- `ntfs_bdev_read()` synchronously reads from a block device into a caller buffer.
- `ntfs_bdev_write()` writes a caller buffer into the block device's address-space folios and marks them dirty.

Core mechanics:
- Reads require 512-byte sector alignment for `start`.
- Non-vmalloc read buffers use `bdev_rw_virt()` with `REQ_OP_READ | REQ_META | REQ_SYNC`.
- Vmalloc read buffers are filled by one or more bios using `bio_add_vmalloc_chunk()`, chained when the current bio cannot accept more data.
- Writes go through `sb->s_bdev->bd_mapping`, reading each target folio, copying the relevant byte range, marking it uptodate and dirty, then dropping the folio.

Important invariants:
- Direct read offsets are sector-based; write offsets are page-cache based.
- The write helper assumes the target block-device folios can be read before modification.
- The vmalloc read path must handle multi-bio chunking for large buffers.

Notable risks:
- `ntfs_bdev_read()` checks `if (op == REQ_OP_READ)` before `invalidate_kernel_vmap_range()`, but `op` includes flags, so this condition is false and the vmalloc read buffer is not invalidated through that branch.
- `ntfs_bdev_write()` returns after the first folio read error and does not roll back prior dirty folios.
