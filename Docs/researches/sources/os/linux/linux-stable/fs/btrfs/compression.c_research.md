# File Research: sources/os/linux/linux-stable/fs/btrfs/compression.c

## Purpose
Implements Btrfs compressed I/O orchestration: compressed read/write bio allocation, compressed folio caching, compression workspace management, algorithm dispatch, inline decompression, and the sampling heuristic used to decide whether compression is worthwhile.

## Main Responsibilities
- Map Btrfs compression types to strings and validate compression type names.
- Allocate and free `compressed_bio` instances from `btrfs_compressed_bioset`.
- Cache single-page compression folios in a global shrinker-backed pool.
- Submit compressed write bios and complete compressed read/write end I/O.
- Build compressed read bios using separate folios for on-disk compressed bytes, then decompress into the original caller bio.
- Opportunistically add readahead pages from the same compressed extent.
- Manage compression workspaces for heuristic, zlib, lzo, and zstd implementations.
- Dispatch compression/decompression to algorithm-specific implementations.
- Implement statistical compressibility heuristics over sampled page-cache data.
- Parse compression level suffixes.

## Key Details
`btrfs_submit_compressed_read()` looks up the compressed extent map, allocates compressed folios sized to `em->disk_num_bytes`, wires the original bio through `cb->orig_bbio`, optionally extends readahead, and submits the compressed bio. End I/O calls `btrfs_decompress_bio()`, completes the original bio, and frees compressed folios.

`btrfs_compress_bio()` allocates a write `compressed_bio`, clamps/defaults the compression level, gets a workspace, calls the selected compressor, and cleans up on failure.

Workspace management uses preallocation for forward progress, waitqueues under allocation pressure, and `memalloc_nofs_save()` around allocator calls that may use vmalloc.

The heuristic samples up to one 128 KiB logical extent using 16-byte samples every 256 bytes, then checks repeated patterns, byte-set size, core byte-set size, and Shannon entropy.

## Risks And Invariants
- Invalid compression dispatch paths use `BUG()` after earlier validation assumptions.
- `compr_pool` is global, spinlock protected, and drained by a shrinker.
- Compressed read readahead is disabled for subpage sectors and block-size-greater-than-page-size cases.
- `btrfs_decompress_buf2page()` handles large folios by deriving file offsets from the folio, not only `bv_page`.
- On compressed write completion, mapping errors are propagated with `mapping_set_error()`.
