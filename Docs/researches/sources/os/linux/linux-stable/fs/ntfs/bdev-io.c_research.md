# File Research: sources/os/linux/linux-stable/fs/ntfs/bdev-io.c

Purpose: Direct block-device I/O helpers for NTFS metadata paths.

Key responsibilities:
- `ntfs_bdev_read()` reads byte ranges from a block device using synchronous metadata BIOs. It requires 512-byte sector alignment and uses `bdev_rw_virt()` for non-vmalloc buffers; vmalloc buffers are handled by BIOs built from vmalloc chunks.
- `ntfs_bdev_write()` writes a byte range through the block device page cache by reading target folios, copying into them, marking them uptodate and dirty, and releasing them.

Important behavior:
- Read path sets `REQ_META | REQ_SYNC`.
- Vmalloc read path chains BIOs if one BIO cannot accept the remaining vmalloc chunk.
- After vmalloc read, `invalidate_kernel_vmap_range()` is called.
- Write path does not submit synchronously; it marks block-device mapping folios dirty.

Risk notes:
- `ntfs_bdev_read()` rejects unaligned starts but does not explicitly reject unaligned sizes.
- `ntfs_bdev_write()` assumes `start + size` arithmetic is valid and does not perform sector-alignment checks.
- Write path depends on later writeback for persistence.
