# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/blkptr.c

## Scope

Implements encoding and decoding for embedded-data ZFS block pointers, where small payloads are stored inside the `blkptr_t` rather than referenced by DVAs.

Read completely: 152 lines.

## Main APIs

- `encode_embedded_bp_compressed()` clears and initializes an embedded block pointer, records compression, byte order, logical size, physical size, and packs payload bytes into payload words.
- `decode_embedded_bp_compressed()` extracts the packed byte stream from an embedded block pointer.
- `decode_embedded_bp()` decodes and, if needed, decompresses an embedded payload into a caller-provided buffer.

## Control Flow

Encoding treats the payload as little-endian byte slots within selected 64-bit words of the block pointer. It skips non-payload words using `BPE_IS_PAYLOADWORD()`. Decoding reverses that process and optionally calls `zio_decompress_data_buf()` when compression is enabled.

## Dependencies

Uses block pointer bitfield macros from ZFS headers, embedded block pointer layout macros, ZIO compression constants, and the ZIO decompression helper.

## Invariants And Risks

- Compressed payload size must not exceed `BPE_PAYLOAD_SIZE`.
- Logical size must fit the caller buffer in `decode_embedded_bp()`, otherwise `ENOSPC` is returned.
- Compression metadata must be valid and within `ZIO_COMPRESS_FUNCTIONS`.
- Payload packing assumes byte-stream semantics independent of the block pointer’s byte order.
