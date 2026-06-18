# File Research: sources/local-fs/erofs-utils/lib/compress.c

## Purpose
Core EROFS compression writer. It builds compressed data extents, handles inline tail packing, fragment packing/dedupe, pcluster sizing, compact/full/extent index generation, optional multithreaded compression, directory compression, and compression algorithm initialization/config metadata.

## Main Structures
- `struct z_erofs_compress_ictx`: per-inode compression context.
- `struct z_erofs_compress_sctx`: per-segment compression context.
- `struct erofs_compress_cfg`: compressor handle plus parameter set and on-disk algorithm type.
- `struct z_erofs_mgr`: compression manager with configured compressors and, in MT builds, fragment slots.
- `struct z_erofs_extent_item`: in-memory compressed/raw/fragment extent list node.

## Important Flow
- `erofs_prepare_compressed_file()`: initializes inode compression state, chooses compressor config, determines data alignment and max compressed extent size, and allocates/chooses compression context.
- `erofs_bind_compressed_file_with_fd()`: binds a source fd/vfile offset to the compression context.
- `erofs_begin_compressed_file()`: computes fragment tail hash, optionally finds matching tail fragments, handles all-fragment files, and queues MT work when enabled.
- `erofs_write_compressed_file()`: single-thread compression path; allocates data buffer, compresses segment, and commits metadata/data.
- `erofs_commit_compressed_file()`: commits fragments, writes indexes, checks space savings, finalizes dedupe commits, updates inode layout and block counts.
- `z_erofs_compress_init()` / `z_erofs_compress_exit()`: initialize compressor configs, feature bits, compression config metadata, pcluster limits, MT state, and free resources.

## Compression Details
- `__z_erofs_compress_one()` decides among compressed pcluster, raw block, inline pcluster, fragment packing, and no-compression fallback.
- `z_erofs_compress_dedupe()` searches existing dedupe windows and emits partial extents when matched.
- `write_uncompressed_block()` supports interlaced uncompressed pclusters.
- `tryrecompress_trailing()` attempts a smaller trailing pcluster for inline/tail efficiency.
- Fragment packing integrates with `fragments.c` and marks `Z_EROFS_ADVISE_FRAGMENT_PCLUSTER`.
- Index writing supports legacy full indexes, compacted 2B/4B indexes, big pcluster encoding, 48-bit encoded extents, and simplified all-fragment files.

## Multithreading
- Enabled by `EROFS_MT_ENABLED`.
- Workqueue TLS owns per-worker queue, destination buffer, and compressor handles.
- `z_erofs_mt_compress()` segments files and queues work.
- `erofs_mt_write_compressed_file()` waits for workers, merges segment extents, performs cross-segment dedupe where possible, and commits output.
- Force-on dedupe disables MT because MT dedupe is not implemented.

## Interactions
- Uses `compressor.c` registry/backends, `dedupe.c`, `dedupe_ext.c`, `fragments.c`, `cache.c`, `block_list.c`, `compress_hints.c`, `metabox`, importer params, and global config.
- Writes compression algorithm config metadata read later by `decompress.c`.

## Notes
This is the highest-complexity file in the group. It is the main bridge between source file data and EROFS compressed on-disk metadata.
