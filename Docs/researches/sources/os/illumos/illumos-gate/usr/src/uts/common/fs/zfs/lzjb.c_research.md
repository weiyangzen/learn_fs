# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lzjb.c

## Purpose

Provides ZFS’s private deterministic copy of the LZJB compression algorithm for on-disk-format stability and deduplication consistency.

## Main APIs

- `lzjb_compress(void *s_start, void *d_start, size_t s_len, size_t d_len, int n)`: compresses source into destination and returns compressed size, or original source length if output would overflow.
- `lzjb_decompress(void *s_start, void *d_start, size_t s_len, size_t d_len, int n)`: decompresses into a fixed-size destination and returns 0 or -1 for invalid back-reference offset.

## Core Behavior

- Uses 3-byte minimum matches, 6 match-length bits, 10 offset bits, and a 1024-entry Lempel table.
- Compression initializes the Lempel table to zero for deterministic output.
- Emits a copymap byte for each group of literal/match decisions.
- Compression bounds output against destination space and falls back by returning `s_len` if compression would not fit.
- Decompression follows copymap bits and copies either literal bytes or back-referenced match runs until destination is filled.

## Dependencies

- `<sys/types.h>` and `<sys/param.h>` for illumos types and `NBBY`.

## Risks And Notes

- This copy is intentionally separate from common OS compression code because changes would affect ZFS on-disk compatibility.
- Decompression trusts compressed source length less than destination length; it primarily bounds destination writes and validates back-reference origin.
- The `n` argument is unused in both functions.
