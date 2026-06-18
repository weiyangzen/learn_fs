# File Research: sources/local-fs/f2fs-tools/fsck/segment.c

Provides userspace block allocation, file read/write, sload file population, extent recalculation, and host-managed zoned update support.

Key responsibilities:
- `reserve_new_block()` finds a free main-area block, updates segment validity maps, SIT/main bitmaps, valid block/node/inode counters, dirty state, and SSA summary.
- `new_data_block()` allocates a data block for a dnode and updates inode block accounting.
- `f2fs_quota_size()` reads quota inode size.
- `f2fs_read()` reads file contents through F2FS node mapping, handling partial block reads and stopping at `NULL_ADDR` / `NEW_ADDR`.
- `f2fs_write_ex()` is the common write engine behind normal writes, compressed-data writes, and address-tag writes (`COMPRESS_ADDR`, `NEW_ADDR`, `NULL_ADDR`).
- `bulkread()` retries interrupted host reads and reports EOF for compression ingestion.
- `f2fs_fix_mutable()` fills mutable compressed-cluster tail blocks with `NEW_ADDR` unless compression is readonly.
- `update_largest_extent()` scans data block addresses and writes the largest consecutive extent into the inode extent cache.
- `f2fs_build_file()` copies a host regular file into the image, with inline-data support, optional sload compression, normal block writes, extent update, and free segment refresh.
- `update_block()` handles in-place block replacement normally, but on host-managed zoned devices relocates old blocks to a new free block and updates SIT, SSA, and node/NAT references.

Important interactions:
- Used by `sload.c` to materialize host files into the F2FS image.
- Used by fsck/repair paths for allocation and zoned-device copy-on-write style updates.
- Tightly depends on node traversal (`get_dnode_of_data()`), NAT lookup, SIT segment entries, summary entries, and `f2fs_io_type_to_rw_hint()`.

Behavioral notes:
- For readonly F2FS feature images, allocation maps node and data writes into hot node/data segment choices.
- Compression write path creates a `COMPRESS_ADDR` header block, writes compressed payload, and adjusts `i_compr_blocks` / `i_blocks`.
- Many failures are handled by `ASSERT`, so callers generally do not get recoverable error handling after deep metadata corruption or I/O failure.
