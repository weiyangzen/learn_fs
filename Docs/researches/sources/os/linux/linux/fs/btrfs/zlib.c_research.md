# File Research: sources/os/linux/linux/fs/btrfs/zlib.c

## Purpose
Implements the Btrfs zlib compression backend: workspace allocation/freeing, compressed-bio creation, compressed-bio decompression, and single-sector inline decompression.

## Workspace Model
`struct workspace` contains:
- `z_stream strm`
- a zlib workspace allocation
- a scratch buffer
- requested compression level
- list linkage for the common compression workspace manager

`zlib_alloc_workspace()` allocates a zlib deflate/inflate workspace large enough for both directions. It also allocates a scratch buffer:
- normally `fs_info->sectorsize`
- `4 * PAGE_SIZE` when s390 DFLTCC hardware acceleration benefits from larger input buffers and the minimum folio size is too small

`zlib_get_workspace()` obtains a generic Btrfs compression workspace and records the requested level. `zlib_free_workspace()` frees zlib internals, scratch buffer, and wrapper.

## Compression Flow
`zlib_compress_bio()`:
- Initializes deflate with the workspace level.
- Allocates compressed-output folios with `btrfs_alloc_compr_folio()`.
- Reads filemap folios through `btrfs_compress_filemap_get_folio()`.
- Either maps folio input directly or copies input into the larger scratch buffer for s390 hardware acceleration.
- Deflates with `Z_SYNC_FLUSH`, then finishes with `Z_FINISH`.
- Adds full or partial output folios to the compressed bio.
- Returns `-E2BIG` if compression expands beyond input or cannot fit output into the target bio.
- Returns `-EIO` for zlib stream failures and `-ENOMEM` for allocation failures.

The compressor abandons work early if compressed output is already larger after more than two sectors of input or total output reaches input length.

## Decompression Flow
`zlib_decompress_bio()`:
- Maps compressed bio folios one by one.
- Detects plain deflate streams without preset dictionaries and skips zlib header/adler checking by using negative `wbits`.
- Inflates into the workspace buffer.
- Copies decompressed ranges into target pages via `btrfs_decompress_buf2page()`.
- Switches input folios when the current folio is exhausted.
- Logs and returns `-EIO` on invalid stream or incomplete decompression.

`zlib_decompress()` handles a small compressed buffer into one destination folio. It expects input/output to fit within sector-sized buffers, inflates once with `Z_FINISH`, copies exactly `destlen`, and zero-fills any short output before returning `-EIO`.

## Hardware-Specific Path
`need_special_buffer()` checks zlib DFLTCC support and Btrfs minimum folio size. `copy_data_into_buffer()` gathers filemap data into the workspace buffer so s390 hardware acceleration sees a larger contiguous input region.

## Exported Compression Levels
`btrfs_zlib_compress` advertises:
- min level: 1
- max level: 9
- default: `BTRFS_ZLIB_DEFAULT_LEVEL`

## Risk and Testing Signals
Coverage should include:
- Compression expansion fallback to uncompressed I/O.
- Direct folio input versus special-buffer input.
- Multi-folio compressed output.
- Header-skipping decompression path.
- Short or corrupt compressed streams zero-filling destination tails.
- Sector-size and larger-folio configurations.
