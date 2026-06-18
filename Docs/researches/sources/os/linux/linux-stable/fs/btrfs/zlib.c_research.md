# File Research: sources/os/linux/linux-stable/fs/btrfs/zlib.c

## Purpose

`zlib.c` implements the Btrfs zlib compression backend: workspace allocation, bio compression, compressed bio decompression, and single-folio decompression.

## Main Structures

- `struct workspace`
  - zlib `z_stream`
  - workspace input/output buffer
  - buffer size
  - list node for Btrfs compression workspace pooling
  - selected compression level

## Main Functions

- `zlib_get_workspace()`
  - Gets a generic Btrfs zlib workspace and records the requested level.
- `zlib_alloc_workspace()`
  - Allocates zlib deflate/inflate workspace memory.
  - Allocates a buffer sized for sectorsize or a larger s390 DFLTCC-friendly buffer.
- `zlib_free_workspace()`
  - Frees zlib workspace memory, temporary buffer, and wrapper object.
- `need_special_buffer()`
  - Detects when s390 hardware zlib acceleration benefits from a 4-page staging buffer.
- `copy_data_into_buffer()`
  - Copies filemap data into the workspace buffer for DFLTCC acceleration.
- `zlib_compress_bio()`
  - Compresses file data into a compressed bio.
  - Maps input folios or uses the workspace staging buffer.
  - Allocates compressed output folios.
  - Aborts with `-E2BIG` if compressed output is not beneficial or cannot fit.
- `zlib_decompress_bio()`
  - Inflates compressed bio folios into target pages using `btrfs_decompress_buf2page()`.
  - Supports raw deflate optimization by inspecting the zlib header and skipping Adler32 when safe.
- `zlib_decompress()`
  - Inflates a small compressed buffer into one destination folio.
  - Zero-fills any missing output on failure/short decompression.
- `btrfs_zlib_compress`
  - Advertises min, max, and default zlib compression levels.

## Important Details

- Compression uses `Z_SYNC_FLUSH` while feeding input and `Z_FINISH` to complete the stream.
- The backend gives up early if the compressed stream grows beyond the original data.
- Output folios are added directly to the compressed bio as they fill.
- Decompression validates that the expected output length was produced; otherwise it returns `-EIO`.
- NOFS-sensitive allocation appears through the broader compression path; this backend uses `GFP_NOFS` for compressed folios.
- Folio mappings are paired carefully with `kunmap_local()` and `folio_put()`.

## Dependencies

This file depends on Linux zlib/zutil APIs, folio/page-cache helpers, bio helpers, and Btrfs compression helpers from `compression.h`, inode metadata from `btrfs_inode.h`, filesystem sizing from `fs.h`, and subpage support.

## Research Notes

The zlib backend is conservative: it prioritizes correctness, bounded output, and hardware-aware buffering. Key failure modes are allocation failure, zlib stream errors, compressed output larger than input, and short decompression.
