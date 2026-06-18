# File Research: sources/os/linux/linux/fs/nilfs2/alloc.h

`alloc.h` declares NILFS2’s persistent allocator interface and cache structures.

Key API:
- `nilfs_palloc_entries_per_group()` computes entries per group from inode block size: one bitmap block worth of bits.
- Initialization, entry-block lookup, entry offset, and maximum-entry counting functions.
- `struct nilfs_palloc_req` carries the requested/allocated entry number plus descriptor, bitmap, and entry buffer heads used by prepare/commit/abort operations.
- Allocation/free transaction functions: prepare/commit/abort allocation, prepare/commit/abort free, and batch free.
- Bit operation aliases bind NILFS allocation bitmaps to ext2 atomic little-endian bit operations and Linux little-endian find-bit helpers.
- `struct nilfs_bh_assoc` stores a cached block offset and buffer head.
- `struct nilfs_palloc_cache` holds cached descriptor, bitmap, and entry buffers protected by a spinlock.

The header exposes setup, clear, and destroy helpers for attaching allocator caches to NILFS metadata inodes.
