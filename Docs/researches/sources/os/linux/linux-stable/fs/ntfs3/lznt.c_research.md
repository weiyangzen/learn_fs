# File Research: sources/os/linux/linux-stable/fs/ntfs3/lznt.c

## Role

NTFS LZNT1 compression and decompression support. LZNT1 is used for traditional NTFS compressed files, operating on 4 KiB chunks with packed literal/match groups.

## Key Structures and Constants

- `LZNT_CHUNK_SIZE` is `0x1000`.
- `struct lznt_hash` stores two recent candidates per hash bucket for standard compression.
- `struct lznt` stores chunk bounds, selected best match, current maximum match length, mode, and optional hash table.
- `s_max_len[]` and `s_max_off[]` encode the changing LZNT pair layout as the current position advances within a chunk.

## Key Functions

- `get_match_len()` computes bounded bytewise match length.
- `longest_match_std()` uses a 4096-entry rolling hash with two candidates for faster compression.
- `longest_match_best()` does exhaustive prior-position search for slower, stronger compression.
- `make_pair()` and `parse_pair()` pack/unpack LZNT offset/length pairs for the current chunk position.
- `compress_chunk()` emits one compressed or uncompressed LZNT chunk.
  - Groups eight items behind one control byte.
  - Emits literals or two-byte match pairs.
  - Detects all-zero chunks.
  - Falls back to uncompressed chunk format when compression does not fit.
- `decompress_chunk()` expands one compressed chunk, validating pair boundaries and output size.
- `get_lznt_ctx()` allocates standard or best-compression context.
- `compress_lznt()` compresses an input buffer chunk-by-chunk and appends a zero terminator when space allows.
- `decompress_lznt()` parses chunk headers, dispatches compressed versus raw chunks, zero-fills partial chunk gaps, and returns decompressed byte count.

## Error Handling

Decompression rejects too-short streams, chunk sizes beyond the compressed buffer, pair references before the chunk start, malformed pair boundaries, and attempts to emit more than one 4 KiB chunk from a compressed chunk.

## Research Notes

This file contains both compression and decompression, unlike the XPRESS/LZX library files. The compressor returns `0` for all-zero input as a special NTFS compression convention and returns the uncompressed size when compression cannot fit.
