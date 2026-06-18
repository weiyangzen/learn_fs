# File Research: sources/local-fs/btrfs-linux/fs/btrfs/compression.c

## Purpose

Implements Btrfs compression infrastructure for compressed read/write bio handling, compression workspace lifetime management, compressed folio caching, decompression copyout, compression heuristics, and module-level compression initialization/teardown.

## Main Responsibilities

- Maps compression type IDs to strings and validates mount/user compression names.
- Allocates `struct compressed_bio` objects from a dedicated bioset.
- Submits compressed writes and reads through Btrfs bio infrastructure.
- Owns generic workspace managers for heuristic, zlib, and lzo compression, while delegating zstd to its dedicated manager.
- Maintains a global cache of single-page compression folios with shrinker support.
- Implements the sampling-based compression heuristic used before deciding to compress.
- Provides inline/single-buffer decompression and full compressed extent decompression support.

## Key Data And State

- `btrfs_compressed_bioset`: bio pool with space for `struct compressed_bio`.
- `btrfs_compress_types`: string table for none/zlib/lzo/zstd.
- `compr_pool`: global cached compression folio pool with `count`, `thresh`, lock, list, and shrinker.
- `struct heuristic_ws`: workspace for compressibility sampling, byte buckets, and radix-sort scratch buffers.
- `btrfs_compress_levels[]`: per-type compression level metadata, with type 0 representing the heuristic manager.

## Important Functions

- `btrfs_compress_type2str()` and `btrfs_compress_is_valid_type()` expose compression type parsing helpers.
- `btrfs_alloc_compr_folio()` / `btrfs_free_compr_folio()` allocate and recycle compression folios, bypassing the cache for larger-than-page folios.
- `btrfs_submit_compressed_write()` submits already-populated compressed write bios, mainly for encoded writes.
- `btrfs_alloc_compressed_write()` creates a compressed write bio for callers to populate.
- `btrfs_submit_compressed_read()` replaces the original read bio pages with temporary compressed-data folios, optionally adds readahead pages, and submits physical IO.
- `btrfs_compress_bio()` compresses page-cache contents into a compressed write bio using zlib/lzo/zstd.
- `btrfs_decompress_bio()` decompresses a full compressed read bio and zero-fills the original bio remainder on success.
- `btrfs_decompress()` handles smaller inline extent decompression into one destination folio.
- `btrfs_decompress_buf2page()` copies decompressed buffers into the original bio’s target pages while respecting partial requested ranges.
- `btrfs_compress_heuristic()` samples file data and returns a nonzero reason code when compression appears worthwhile.
- `btrfs_compress_str2level()` parses optional `:level` suffixes and clamps to supported algorithm levels.
- `btrfs_init_compress()` / `btrfs_exit_compress()` initialize and destroy the bioset, shrinker, and cached folio pool.

## Control Flow

Compressed reads begin with an ordinary Btrfs read bio whose extent map is compressed. `btrfs_submit_compressed_read()` finds the full compressed extent, creates a separate `compressed_bio`, allocates temporary folios for on-disk compressed bytes, may append compatible readahead pages to the original bio, then submits the compressed bio. End IO calls `btrfs_decompress_bio()`, completes the original bio, releases temporary folios, and drops the compressed bio.

Compressed writes use `btrfs_compress_bio()` to allocate a compressed bio, choose an adjusted compression level, acquire a workspace, call the algorithm-specific compressor, release the workspace, and return the populated compressed bio. End IO finishes the ordered extent, clears page-cache writeback when applicable, frees compressed folios, and releases the bio.

The heuristic path samples up to 128 KiB of input, collecting 16-byte samples every 256 bytes. It checks repeated patterns, byte-set size, core byte-set size covering 90% of the sample, and approximate Shannon entropy before deciding if compression should be attempted.

## Integration Points

- Depends on algorithm implementations through `zlib_*`, `lzo_*`, and `zstd_*` functions declared in `compression.h`.
- Uses extent maps to locate compressed extents and check readahead eligibility.
- Uses ordered extents for compressed write completion.
- Uses Btrfs bio submission and checksum state propagation through `struct btrfs_bio`.
- Ties into kernel shrinkers for cached compression folio reclaim.
- Provides helpers used by defrag and mount option parsing for compression level validation.

## Invariants And Risks

- Compression type is expected to be validated before dispatch; invalid dispatch paths call `BUG()`.
- Workspace acquisition intentionally waits instead of returning allocation failures, relying on preallocation for forward progress.
- Readahead is disabled for subpage and block-size-greater-than-page cases in this path.
- The compressed folio cache assumes order-0 folios with refcount 1 on release.
- `heuristic_collect_sample()` assumes pages are present in the page cache and maps them directly.
- `btrfs_decompress_buf2page()` mutates the original bio iterator as decompressed bytes are copied.

## Testing Notes

Relevant coverage should exercise zlib/lzo/zstd reads and writes, inline decompression, encoded writes, compressed readahead, memory pressure shrinker behavior, level parsing, remount/no-compress races, and heuristic decisions for text, zeroed, repeated, random, and high-entropy data.
