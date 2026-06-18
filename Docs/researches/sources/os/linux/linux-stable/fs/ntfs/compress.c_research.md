# File Research: sources/os/linux/linux-stable/fs/ntfs/compress.c

Purpose: Handles NTFS compressed attribute reads and writes, including LZNT1-style compression/decompression, sparse compression blocks, and compressed-block disk allocation.

Key responsibilities:
- Manages a global decompression buffer with `allocate_compression_buffers()` and `free_compression_buffers()`, protected by `ntfs_cb_lock`.
- `ntfs_decompress()` parses compressed blocks into destination pages, handling uncompressed sub-blocks, compressed phrase/symbol tokens, overlapping phrase copies, incomplete sub-block zero-fill, page finalization, and initialized-size zeroing.
- `ntfs_read_compressed_block()` reads all pages in the compression block containing a requested folio, resolves runlist mappings, reads compressed clusters from the block device mapping, distinguishes sparse/uncompressed/compressed compression blocks, and fills/updates/unlocks page-cache pages.
- Compression write path uses `ntfs_best_match()`, `ntfs_skip_position()`, and `ntfs_compress_block()` to encode 4 KiB sub-blocks.
- `ntfs_write_cb()` compresses one compression block, chooses compressed, sparse-all-zero, or uncompressed storage, punches the old block, allocates new clusters, updates mapping pairs, and submits write BIOs.
- `ntfs_compress_write()` updates compressed file data from an iov iterator by reading all pages in each compression block, copying user data into them, writing the recompressed block, and releasing pages.

Important data and constants:
- Compression block maximum is 64 KiB.
- NTFS sub-block size is 4096 bytes.
- Token type constants distinguish symbol and phrase tokens.
- Match finder uses a hash table and short chain depth limit for write-side compression.
- Predefined compressed zero sequences are used to detect all-zero blocks and represent them as sparse.

Important invariants:
- Decompression requires page size at least 4096.
- Only unnamed `$DATA` compressed attributes are accepted by the read path.
- The global compression buffer is protected while reading/decompressing compressed data; `ntfs_decompress()` unlocks it when safe.
- Pages that were dirty or uptodate are not overwritten during compressed reads.
- Compressed writes operate at full compression-block granularity.

Dependencies:
- Uses attribute/runlist functions from `attrib.c`.
- Uses cluster allocation/freeing and runlist merge from allocation/runlist subsystems.
- Uses MFT dirty marking and file-name dirty state for metadata updates.
- Uses block-device mapping pages for reads and BIOs for writes.

Risk notes:
- Decompression failure returns `-EOVERFLOW` internally and usually becomes `-EIO` at the read entry point if the requested page was not completed.
- `ntfs_compress_block()` is documented as returning 0 on error, but allocation failure returns `-ENOMEM` through an unsigned return type; callers treat nonzero large values as a compression failure condition indirectly.
- `ntfs_write_cb()` punches old clusters before allocating/writing replacement clusters, so failures after punching are metadata-sensitive.
- Compression write path marks folios uptodate/clears dirty for fully processed pages but returns bytes written or negative errno depending on final state.
