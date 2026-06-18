# File Research: sources/local-fs/kdave-linux/fs/btrfs/lzo.c

## Purpose

`lzo.c` implements Btrfs’s LZO compression backend. It allocates compression workspaces, compresses file data into Btrfs’s on-disk LZO segment format, and decompresses both regular compressed extents and inline compressed extents.

## Format

The file documents the Btrfs LZO format:

- A 4-byte little-endian total compressed length header.
- One or more segments.
- Each segment has a 4-byte little-endian payload length followed by compressed data.
- Each segment represents at most one uncompressed sector.
- Segment headers must not cross sector boundaries; padding zeros may be inserted near sector ends.
- Inline LZO extents allow only one segment.

## Workspace

`struct workspace` owns:

- LZO compression memory.
- A decompressed buffer.
- A compressed buffer.
- A list node for workspace pooling.

`lzo_alloc_workspace()` allocates these buffers based on `lzo1x_worst_compress(sectorsize)`. `lzo_free_workspace()` frees them.

## Compression Flow

`lzo_compress_bio()` creates a compressed bio for a file range. It reserves the initial total-size header, then iterates input file folios sector by sector. Each sector is compressed with `lzo1x_1_compress()`, then `copy_compressed_data_to_bio()` writes the segment header, payload, and any required padding into compressed folios queued on the bio.

The code gives up with `-E2BIG` if compression expands beyond acceptable limits, including an early check after more than two sectors. Folio ownership is carefully split: queued folios are released by bio completion, while unqueued output folios are freed locally on failure.

## Decompression Flow

`lzo_decompress_bio()` reads the total compressed length header, validates it against the compressed bio size and maximum compressed extent size, then iterates segment headers and payloads. It copies segment payloads into the workspace, calls `lzo1x_decompress_safe()`, and writes output into target pages through `btrfs_decompress_buf2page()`.

`lzo_decompress()` handles inline compressed data: it validates the total length and single-segment length headers, decompresses into the workspace buffer, copies into the destination folio, and zeros/report-errors on short output.

## Dependencies and Integration

Depends on Linux LZO APIs, Btrfs compression helpers, folio/bio helpers, inode/root diagnostics, and `messages.h`. It exports `btrfs_lzo_compress` with max/default level 1.

## Risk Notes

Important correctness boundaries are segment header validation, sector-boundary padding, compressed length limits, folio offset math, and ownership transfer of compressed folios into bios. Corruption paths return `-EUCLEAN` or `-EIO` with Btrfs error logs.
