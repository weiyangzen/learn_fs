# File Research: sources/local-fs/btrfs-linux/fs/btrfs/lzo.c

## Purpose

Implements Btrfs LZO compression and decompression for regular compressed bios and inline extents.

## Format

Btrfs LZO data starts with a 4-byte little-endian total compressed length. It then contains one or more segments. Each segment has a 4-byte little-endian segment payload length followed by compressed payload. Segment headers never cross sector boundaries, so padding zeros may appear near sector ends. Inline extents allow only one segment.

## Main Responsibilities

- Allocates/frees LZO workspaces: compression memory, decompression buffer, and compressed temporary buffer.
- Compresses filemap data sector-by-sector into compressed folios and queues them into a bio.
- Writes the top-level LZO length after compression completes.
- Rejects compression when output grows too large.
- Decompresses compressed bios by validating top-level length, reading segment headers/payloads across folios, and copying decompressed data to target pages.
- Decompresses inline LZO data into a destination folio.
- Exports Btrfs LZO compression level metadata.

## Key Behaviors and Invariants

- One segment represents at most one sector of uncompressed data.
- Segment headers must fit within a sector; compression pads when fewer than 4 bytes remain.
- Folio ownership transfers to the bio once queued; error cleanup only frees unqueued folios.
- Decompression validates total length against compressed bio size and max compressed extent size, returning corruption or I/O errors for invalid headers/segments.
- Inline decompression expects exact nested length headers and zero-fills short output before returning error.
