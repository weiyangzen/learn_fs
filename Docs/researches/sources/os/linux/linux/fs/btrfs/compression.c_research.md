# File Research: sources/os/linux/linux/fs/btrfs/compression.c

## Purpose

Implements Btrfs compressed I/O orchestration: compressed read/write bio allocation, compressed folio caching, compression workspace management, algorithm dispatch, inline/single-page decompression, and the data sampling heuristic used to decide whether compression is worthwhile.

## Main Responsibilities

- Map Btrfs compression types to strings and validate mount/ioctl compression type names.
- Allocate and free `compressed_bio` instances from `btrfs_compressed_bioset`.
- Cache single-page compression folios in a global shrinker-backed pool.
- Submit compressed write bios and complete compressed read/write end I/O.
- Build compressed read bios using separate folios for on-disk compressed bytes, then decompress into the original caller bio.
- Opportunistically add readahead pages from the same compressed extent to the original bio.
- Manage compression workspaces for heuristic, zlib, lzo, and zstd implementations.
- Dispatch compression/decompression to algorithm-specific implementations.
- Implement statistical compressibility heuristics over sampled page-cache data.
- Parse compression level suffixes.

## Key Types And State

- `static struct bio_set btrfs_compressed_bioset`: bioset whose object layout embeds `struct compressed_bio`.
- `btrfs_compress_types[]`: indexed by `enum btrfs_compression_type`, with entries for none, zlib, lzo, and zstd.
- `compr_pool`: global cache of unused order-0 compression folios, protected by spinlock and drained by shrinker.
- `struct heuristic_ws`: workspace for sampling, byte bucket counting, sorting, and entropy analysis.
- `struct workspace_manager`: per-filesystem workspace idle list, waitqueue, spinlock, free count, and total count.

## Important Functions

- `btrfs_compress_type2str()` returns canonical string names for valid compression enum values.
- `btrfs_compress_is_valid_type()` accepts prefix matches against supported compression names.
- `alloc_compressed_bio()` allocates a Btrfs bio and initializes its embedded `compressed_bio`.
- `btrfs_alloc_compr_folio()` / `btrfs_free_compr_folio()` allocate order-`block_min_order` folios, using the global folio pool only for order-0 folios.
- `end_bbio_compressed_read()` decompresses a completed compressed read and completes the original bio.
- `end_bbio_compressed_write()` finishes ordered extent accounting, clears writeback when applicable, frees compressed folios, and drops the bio.
- `btrfs_submit_compressed_write()` submits a previously populated compressed write bio for encoded writes.
- `btrfs_alloc_compressed_write()` allocates a compressed write bio shell for callers that will populate folios themselves.
- `add_ra_bio_pages()` speculatively adds page-cache folios mapping to the same compressed extent into the original read bio.
- `btrfs_submit_compressed_read()` looks up the extent map, allocates compressed folios, builds the read bio, may extend original bio readahead, and submits.
- `btrfs_get_workspace()` waits for or allocates a compression workspace, with preallocation intended to guarantee forward progress.
- `btrfs_put_workspace()` returns a workspace to the idle list or frees it when too many are cached.
- `btrfs_compress_bio()` compresses page-cache bytes into a new compressed write bio and returns an error pointer if compression is not useful or impossible.
- `btrfs_decompress()` handles inline/small decompression into a destination folio.
- `btrfs_decompress_buf2page()` copies a decompressed buffer into the original bio, advancing only the requested range.
- `btrfs_compress_heuristic()` samples input bytes and classifies data as compressible or not.
- `btrfs_compress_str2level()` parses optional `:<level>` suffixes and clamps to algorithm limits.

## Control Flow

Compressed write path:
1. Caller invokes `btrfs_compress_bio()`.
2. Function allocates `compressed_bio`, chooses/clamps level, gets algorithm workspace.
3. Algorithm-specific compressor fills compressed folios into the bio.
4. Workspace is returned.
5. On success, caller submits the bio later; on failure, compressed folios and bio are cleaned up.

Compressed read path:
1. Caller passes an original `btrfs_bio` covering file-cache destination folios.
2. `btrfs_submit_compressed_read()` looks up the compressed extent map at `file_offset`.
3. It allocates a separate compressed bio and compressed folios sized to `em->disk_num_bytes`.
4. It may extend the original bio with additional readahead pages in the same compressed extent.
5. It submits the compressed bio to the block layer.
6. End I/O decompresses into the original bio and completes it.

Workspace path:
1. Per-filesystem workspace managers are allocated by `btrfs_alloc_compress_wsm()`.
2. Each non-zstd manager tries to preallocate one workspace.
3. `btrfs_get_workspace()` reuses idle workspaces, caps allocations around online CPU count, and waits if necessary.
4. Zstd uses its own manager hooks.

Heuristic path:
1. `heuristic_collect_sample()` samples up to 128 KiB of input at 16-byte reads every 256 bytes.
2. Fast repeated-pattern detection runs first.
3. Buckets count byte frequency.
4. Small byte-set data is accepted as compressible.
5. Core byte set size and Shannon entropy are used to reject uniform/high entropy data or accept low entropy data.

## Concurrency, Locking, And Memory Notes

- `compr_pool` uses a spinlock; the shrinker drains the entire list.
- Workspace managers use a spinlock for idle lists and a waitqueue for allocation pressure.
- Workspace allocation temporarily disables filesystem reclaim via `memalloc_nofs_save()` because algorithm allocators may vmalloc.
- `add_ra_bio_pages()` avoids direct reclaim for readahead bios and uses PSI memstall tracking only when a workingset folio is added.
- Compressed read readahead is disabled for subpage sectors and block-size-greater-than-page-size cases.
- `btrfs_decompress_buf2page()` is careful with large folios because `bv_page->index` may not identify the head folio.

## Error Handling And Invariants

- Invalid compression dispatch cases use `BUG()` after earlier validation assumptions.
- Compressed extent sizes are bounded by header constants from `compression.h`.
- `btrfs_get_workspace()` intentionally does not return allocation errors after manager setup; it waits/retries for forward progress.
- `btrfs_submit_compressed_read()` completes the original bio with a block status on allocation or lookup failure.
- `btrfs_decompress()` asserts inline decompression does not exceed folio size or sectorsize.
- On compressed write completion, mapping errors are propagated through `mapping_set_error()` if block I/O failed.

## Dependencies

- Public declarations and constants in `compression.h`.
- Btrfs bio wrappers from `bio.h`.
- Ordered extent completion from `ordered-data.h`.
- Extent map lookup and compression metadata from `extent_map.h`.
- Page/folio extent state helpers from `extent_io.h` and `subpage.h`.
- Algorithm implementations for zlib, lzo, and zstd.
