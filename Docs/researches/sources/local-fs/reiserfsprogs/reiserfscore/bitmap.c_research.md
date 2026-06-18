# File Research: sources/local-fs/reiserfsprogs/reiserfscore/bitmap.c

Implements in-memory and on-disk ReiserFS block bitmap handling. Basic operations create, expand, shrink, delete, copy, compare, set, clear, test, fill, zero, invert, count, and find zero bits while maintaining `bm_set_bits` and dirty state.

On-disk handling:
- `reiserfs_fetch_ondisk_bitmap()` reads bitmap blocks from the filesystem, following spread-bitmap layout when enabled, copies bytes into memory, validates unused tail bytes/bits, clears out-of-range in-memory bits, and recomputes set-bit count.
- `reiserfs_flush_to_ondisk_bitmap()` writes dirty bitmap contents back, initializes bitmap blocks to `0xff`, copies active bytes, and sets unused tail bits on disk.
- `reiserfs_open_ondisk_bitmap()` validates expected bitmap count, including large-filesystem overflow behavior.
- `reiserfs_create_ondisk_bitmap()` allocates an empty bitmap for new filesystems.
- `reiserfs_close_ondisk_bitmap()` flushes and frees.

Also serializes fsck temporary bitmaps with start/end magic and run-length encoded used/free extents, and saves/validates fsck stage markers.
