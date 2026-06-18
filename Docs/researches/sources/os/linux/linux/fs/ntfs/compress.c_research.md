# File Research: sources/os/linux/linux/fs/ntfs/compress.c

Implements NTFS compressed `$DATA` read and write support, including decompression into page-cache pages, LZNT1-like sub-block compression, compressed-block allocation, and compressed writes.

Key entry points:
- `allocate_compression_buffers()` and `free_compression_buffers()` manage the shared 64 KiB compression buffer.
- `ntfs_read_compressed_block()` reads one or more compression blocks overlapping a locked folio and fills page-cache pages.
- `ntfs_compress_write()` writes user data into compression-block-sized page groups and commits compressed blocks through `ntfs_write_cb()`.

Core mechanics:
- A single global `ntfs_compression_buffer` is protected by `ntfs_cb_lock`.
- `ntfs_decompress()` parses NTFS compression sub-blocks. It handles uncompressed sub-blocks, compressed symbol/phrase tokens, overlapping back-references, incomplete sub-block zero fill, destination page finalization, initialized-size zeroing, and overflow detection.
- `ntfs_read_compressed_block()` computes compression-block-aligned VCN and page ranges, grabs non-dirty cache pages, reads physical clusters through the block device mapping, and distinguishes sparse, uncompressed, and compressed compression blocks.
- Sparse compression blocks are zero-filled without disk reads after the first `LCN_HOLE`.
- Uncompressed compression blocks copy the full block directly from the shared buffer into destination pages.
- Compressed blocks call `ntfs_decompress()`, which unlocks the shared buffer before completing pages.
- The compressor uses a hash-chain match finder (`compress_context`) over 4 KiB sub-blocks, lazy parsing, phrase tokens for matches, symbol tokens for literals, and falls back to uncompressed storage when compressed output is not smaller.
- `ntfs_write_cb()` maps the input pages, compresses each 4 KiB sub-block, recognizes all-zero compressed output as a sparse block, punches the existing compression block run, allocates new clusters for compressed or uncompressed output, updates mapping pairs, then writes bios.
- `ntfs_compress_write()` expands compressed files to compression-block boundaries as needed, faults in the source iterator, reads and locks every page in the affected compression block, overlays user bytes, writes the block, then unlocks/releases pages.

Important invariants:
- NTFS compression block size is derived from the attribute compression unit and must fit the supported maximum of 64 KiB.
- The decompressor assumes `PAGE_SIZE >= 4096`.
- Compressed I/O is only valid for unnamed `$DATA`; other attributes fail the read path.
- Page finalization must zero regions beyond initialized size and mark pages uptodate before unlocking.
- `ntfs_write_cb()` replaces the whole compression block allocation, not just the modified bytes.
- Mapping pairs must be updated after punching and allocating replacement compressed runs.

Notable risks:
- `ntfs_decompress()` calls `ntfs_error(NULL, ...)`; `__ntfs_error()` only marks volume errors when an `sb` is provided, so stream corruption reported here is not tied to a mounted volume.
- The shared compression buffer serializes compressed reads and writes through one mutex.
- `ntfs_compress_block()` documents `0` as error but returns `-ENOMEM` through an unsigned return type on allocation failure; callers treat nonzero large values as compression failure only indirectly through size checks.
- `ntfs_write_cb()` marks filename/MFT dirty even on several error exits after partial metadata operations.
- Compressed writes rewrite whole compression blocks and depend on page-cache state for unchanged bytes; stale or failed page reads can abort the entire block write.
