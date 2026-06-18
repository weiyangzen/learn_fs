# File Research: sources/os/linux/linux/fs/ntfs3/lznt.c

## Role

Implements NTFS LZNT1 compression and decompression for NTFS compressed file attributes. It supports standard hash-assisted compression, best-match compression, and chunked decompression.

## Key Structures and Constants

- `LZNT_CHUNK_SIZE` is 0x1000 bytes.
- `LZNT_ERROR_ALL_ZEROS` is an internal compression result indicating an all-zero input buffer.
- `struct lznt_hash` stores two previous match candidates per hash bucket.
- `struct lznt` tracks current uncompressed chunk bounds, best match pointer, maximum match length, compression mode, and optional hash table.
- `s_max_len[]` and `s_max_off[]` encode LZNT1’s changing offset/length bit split by current chunk position.

## Compression

- `get_match_len()` measures a bytewise match up to a maximum.
- `longest_match_std()` uses a 4096-entry hash table with two candidates per bucket.
- `longest_match_best()` scans prior bytes for best compression at high CPU cost.
- `make_pair()` packs offset/length into a 16-bit LZNT token.
- `compress_chunk()` emits control-byte groups of eight items, literals or packed pairs, falls back to an uncompressed chunk when compressed output would not fit, and reports all-zero chunks specially.
- `get_lznt_ctx()` allocates a context sized for standard or best compression.
- `compress_lznt()` compresses all 4 KiB chunks, writes a zero terminator when space permits, returns final compressed size, returns `0` for all-zero input, and returns `unc_size` when compression cannot fit usefully.

## Decompression

- `parse_pair()` unpacks offset/length from a token.
- `decompress_chunk()` decodes one compressed chunk, validates token boundaries and backward offsets, truncates final match at the output end, and rejects writes beyond one LZNT chunk.
- `decompress_lznt()` reads chunk headers, handles compressed and uncompressed chunks, zero-fills short chunks as needed, stops at output full/input end/zero header, and returns bytes decompressed or `-EINVAL`.

## Dependencies

Uses Linux kernel, slab, string, type headers, `debug.h`, and `ntfs_fs.h`.

## Research Notes

This file covers classic NTFS compression, distinct from WOF LZX/XPRESS system compression. Decompression has explicit malformed-stream checks for chunk size, token availability, backward offset validity, and output chunk limits.
