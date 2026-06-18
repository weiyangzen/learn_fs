# File Research: sources/os/linux/linux/fs/btrfs/lzo.c

This file implements Btrfs LZO compression and decompression for compressed extents and inline compressed extents.

On-disk format:
- A 4-byte little-endian extent header records total compressed size including the header.
- Each segment has a 4-byte little-endian segment length followed by compressed payload.
- Each segment represents at most one filesystem sector of uncompressed data.
- Segment headers must not cross sector boundaries; up to three zero padding bytes may be inserted at the end of a sector.
- Inline LZO extents support only one segment.

Workspace management:
- `struct workspace` owns LZO working memory, a decompression buffer, a compression buffer, and a list node.
- `lzo_alloc_workspace()` allocates LZO memory and buffers sized by `lzo1x_worst_compress(sectorsize)`.
- `lzo_free_workspace()` frees workspace allocations.

Compression path:
- `lzo_compress_bio()` compresses file data one sector at a time from the inode mapping.
- It allocates compressed folios, reserves space for the total-size header, writes segment headers and payloads, pads sector tails when needed, and queues folios into the compressed bio.
- `copy_compressed_data_to_bio()` enforces segment-header alignment, copies compressed payload in sector-bounded chunks, checks output growth against the original length, and manages folio rollover.
- Compression aborts with `-E2BIG` when data grows too much, including an early check after more than two sectors.
- On success, the first header is patched with the final compressed byte count.

Decompression path:
- `lzo_decompress_bio()` reads the total-size header, validates it against the compressed bio size and maximum compressed extent size, then iterates all segments.
- Segment payloads are copied into the workspace buffer even when they span folios.
- `lzo1x_decompress_safe()` expands each segment into the workspace buffer, then `btrfs_decompress_buf2page()` copies data into destination pages.
- Corrupt headers return `-EUCLEAN`; oversized segments and LZO failures return I/O-style errors with Btrfs error messages.
- `lzo_decompress()` handles inline extents, validating the outer and segment length headers before decompressing into a destination folio.

Important invariants:
- Segment headers never cross sector boundaries.
- A regular compressed extent may contain multiple sector-sized segments; an inline extent is validated as a single segment.
- Output folios already queued into a bio are released by bio completion; only unqueued folios are freed locally on error.
- The exported compression level descriptor advertises only level 1/default 1 for LZO.

Cross-file relationships:
- Integrates with `compression.h` workspace dispatch and compressed bio helpers.
- Uses Btrfs folio allocation/free helpers, inode/root identifiers for error reporting, and generic LZO library calls.
