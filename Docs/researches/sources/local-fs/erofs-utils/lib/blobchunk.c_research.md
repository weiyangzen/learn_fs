# File Research: sources/local-fs/erofs-utils/lib/blobchunk.c

## Purpose
Implements blob/chunk-based file storage for mkfs/import paths, including chunk dedupe, sparse-hole chunks, external blob device handling, tar source mapping, and chunk index writing.

## Main Structures
- `struct erofs_blobchunk`: hash/list entry containing SHA-256, device id, chunk size or source offset, and block address.
- Global `blob_hashmap`: dedupe map keyed by chunk SHA-256.
- Global `erofs_holechunk`: sentinel chunk for holes.
- `unhashed_blobchunks`: chunks that reference pre-existing external/tar data without content hashing.

## Important Functions
- `erofs_blob_getchunk()`: hashes chunk data, deduplicates unless disabled, writes new chunks to the blob file, pads to block size, and records hash entries.
- `erofs_inode_fixup_chunkformat()`: upgrades chunk format to 48-bit if device/block addresses exceed 32-bit capacity.
- `erofs_write_chunk_indexes()`: serializes in-memory chunk pointers into on-disk block-map or chunk-index records, including block-list output.
- `erofs_blob_mergechunks()`: coalesces chunk index granularity when contiguous chunks allow a larger chunk size.
- `erofs_blob_write_chunked_file()`: converts a regular file into chunk-based extents, detecting holes with `SEEK_DATA`, deduping chunks, aligning data if needed, and choosing merge size.
- `erofs_write_zero_inode()`: creates a chunk-based inode entirely backed by null-address chunks.
- `tarerofs_write_chunkes()`: builds chunk indexes for tar-imported data, supporting extra device mode and 48-bit addressing.
- `erofs_mkfs_dump_blobs()`: appends the temporary blob data into the final image unless external devices are used.
- `erofs_blob_init()` / `erofs_blob_exit()`: open temp/output blob file, initialize hash map, insert zero-chunk entry, and free all state.

## Interactions
- Uses SHA-256, generic hashmap, buffer manager allocation, block-list source map writing, temp files, and global mkfs config.
- Cooperates with `data.c` chunk-based mapping and EROFS chunk index on-disk formats.

## Notes
Zero-filled chunks are treated as holes by inserting the zero hash with `EROFS_NULL_ADDR`.
