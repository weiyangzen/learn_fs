# File Research: sources/windows/winbtrfs/src/compress.c

## Role

`compress.c` provides zlib, LZO, and ZSTD compression/decompression support plus the filesystem-level `write_compressed` path that turns file data into Btrfs compressed extents.

## Codec Support

- zlib:
  - `zlib_alloc`/`zlib_free` allocate from paged pool using `ALLOC_TAG_ZLIB`.
  - `zlib_compress` wraps `deflateInit`, `deflate(..., Z_FINISH)`, and `deflateEnd`.
  - `zlib_decompress` wraps `inflateInit`, `inflate(..., Z_NO_FLUSH)`, and `inflateEnd`.
- LZO:
  - Defines an `lzo_stream` cursor/error structure and LZO1X constants.
  - `do_lzo_decompress` implements bytecode-style LZO decompression with bounds checks on input, output, and backreferences.
  - `lzo_decompress` handles Btrfs' per-page LZO framing, page padding, and zero-fills short decompressed pages.
  - `lzo_do_compress`, `lzo1x_1_compress`, and `lzo_compress` implement old LGPL LZO compression and Btrfs page framing.
- ZSTD:
  - Uses `ZSTD_STATIC_LINKING_ONLY` and ZSTD custom memory callbacks backed by paged pool.
  - `zstd_decompress` uses a `ZSTD_DStream`.
  - `zstd_compress` uses a `ZSTD_CStream`, clamps `windowLog` to Btrfs' maximum of 17, and reports remaining output space.

## `write_compressed`

The filesystem integration path does the following:

- Chooses compression type from mount options, per-FCB compression property, and filesystem incompat flags.
- Calls `excise_extents` to remove the old data range.
- Splits the write into `COMPRESSED_EXTENT_SIZE` chunks, 128 KiB each.
- Queues one compression calculation job per chunk through `add_calc_job_comp`.
- Drains jobs, waits for each completion event, and propagates any codec failure.
- Keeps compressed output only if it saves at least one sector; otherwise stores that chunk uncompressed.
- Sets LZO/ZSTD incompat flags when those compression types are actually used.
- Sector-aligns compressed output buffers and zero-pads alignment slack.
- If the first 128 KiB of a file is incompressible and compression was not forced, marks the inode `BTRFS_INODE_NOCOMPRESS`.
- Concatenates all chosen parts into a contiguous buffer.
- Finds or allocates a suitable data chunk, reserves free space with `space_list_subtract`, and writes the buffer through `write_data_complete`.
- Calculates sector checksums with `do_calc_job` unless the inode has `BTRFS_INODE_NODATASUM`.
- Creates `EXTENT_DATA`/`EXTENT_DATA2` entries for each compressed or uncompressed part via `add_extent_to_fcb`.
- Adds delayed extent references with `add_changed_extent_ref`.
- Marks extents and inode state dirty and calls `mark_fcb_dirty`.

## Dependencies

- Includes `btrfs_drv.h`, `zlib/zlib.h`, and `zstd/lib/zstd.h`.
- Relies on driver allocation, write, checksum, chunk, space-list, rollback, and extent-ref APIs declared in `btrfs_drv.h`.
- Used by write and FSCTL code paths for compressed data writes; read and send paths use the decompression helpers.

## Research Notes

- The file contains third-party-derived codec code: LZO decompression notes credit libavcodec and LZO compression notes credit LZO 0.22.
- `write_compressed` mixes CPU work, allocation, chunk-space reservation, physical I/O, checksum generation, and metadata updates, so rollback and cleanup behavior is important.
- The compression decision is per 128 KiB part; a single logical write can produce a mix of compressed and uncompressed extents.
- ZSTD is constrained to Btrfs' expected window size, preventing creation of extents that Linux/Btrfs-compatible readers would reject.
