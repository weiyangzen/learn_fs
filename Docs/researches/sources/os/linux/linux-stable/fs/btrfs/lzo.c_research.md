# File Research: sources/os/linux/linux-stable/fs/btrfs/lzo.c

## Summary
Implements Btrfs LZO compression and decompression, including workspace allocation, on-disk segment format handling, compressed bio construction, compressed bio decompression, and inline extent decompression.

## Main Responsibilities
- Allocates/frees LZO compression workspaces.
- Compresses filemap data into Btrfs compressed bio folios.
- Emits Btrfs LZO headers, segment headers, payloads, and sector padding.
- Decompresses regular compressed bios into target pages.
- Decompresses inline LZO extents into a destination folio.
- Defines supported LZO compression level metadata.

## Key APIs
- `lzo_alloc_workspace()`.
- `lzo_free_workspace()`.
- `lzo_compress_bio()`.
- `lzo_decompress_bio()`.
- `lzo_decompress()`.
- `btrfs_lzo_compress`.

## Important Behavior
Btrfs LZO extents start with a 4-byte little-endian total compressed length, followed by one or more segments. Each segment has a 4-byte little-endian payload length and at most one sector of uncompressed data. Segment headers must not cross sector boundaries, so compression pads up to 3 zero bytes when needed.

Compression reserves an output folio, writes the total-length header placeholder, compresses at most one sector at a time with `lzo1x_1_compress()`, copies each compressed segment into the output bio, and finally writes total compressed size into the first folio. If compressed output grows beyond allowed limits or grows larger than input after the early threshold, it returns `-E2BIG`.

Decompression validates the total LZO length against compressed bio size and maximum compressed extent size. It walks segment headers/payloads across folios, copies payloads into workspace memory, calls `lzo1x_decompress_safe()`, and forwards decompressed buffers to `btrfs_decompress_buf2page()`.

Inline decompression expects exactly one compressed segment after the total-size and segment-size headers. It validates source length, decompresses into the workspace buffer, copies to the destination folio, and zero-fills plus returns `-EIO` if output is shorter than requested.

## State and Synchronization
Workspace objects contain separate LZO scratch memory, decompressed buffer, compressed buffer, and list linkage. Folios queued into bios are owned by bio endio cleanup; only unqueued output folios are freed directly on error.

## Risks
The format parser is sensitive to corrupted lengths, sector-boundary padding, folio switching, and maximum segment size checks. Error handling relies on precise ownership transfer of folios to bios.
