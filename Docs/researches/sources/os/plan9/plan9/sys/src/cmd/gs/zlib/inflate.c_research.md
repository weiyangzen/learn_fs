# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/inflate.c

## Purpose
Implements zlib decompression: stream initialization/reset, zlib/gzip/raw wrapper handling, deflate block decoding, dictionary support, synchronization recovery, state copying, and cleanup.

## Main API Surface
Exports:
- `inflateReset`
- `inflateInit2_`
- `inflateInit_`
- `inflate`
- `inflateEnd`
- `inflateSetDictionary`
- `inflateSync`
- `inflateSyncPoint`
- `inflateCopy`

Internal helpers:
- `fixedtables`
- `updatewindow`
- `syncsearch`
- Optional `makefixed` generator.

## Wrapper Handling
`inflateInit2_` interprets `windowBits`:
- Negative values request raw deflate with no zlib/gzip wrapper.
- Positive values enable zlib wrapping.
- With `GUNZIP`, larger encoded values can enable gzip header/trailer handling.

The `HEAD` state validates zlib headers or gzip magic. Gzip-specific states parse flags, timestamp, OS byte, extra field, original name, comment, and header CRC. Trailer validation checks Adler-32 for zlib or CRC32 plus length for gzip.

## Deflate State Machine
The main `inflate()` switch handles:
- Stored blocks: length/complement validation and byte copy.
- Fixed-Huffman blocks: precomputed fixed tables.
- Dynamic-Huffman blocks: code-length table parsing and `inflate_table()` table construction.
- Literal, match length, distance, and copy states.
- End-of-block, checksum, done, bad, memory, and sync states.

For large enough buffers, `LEN` delegates to `inflate_fast()`.

## Sliding Window
`updatewindow()` lazily allocates the sliding window only when needed. It records the last `2^wbits` output bytes in circular form, enabling future distance references and dictionary injection.

## Dictionary and Sync
`inflateSetDictionary()` validates the dictionary Adler-32 and loads dictionary bytes into the window. `inflateSync()` scans for the byte pattern `00 00 ff ff` to recover at flush points, preserving total counters across reset. `inflateSyncPoint()` identifies a state useful for PPP-style sync flush handling.

## Error Handling
The implementation sets `strm->msg` for malformed headers, bad block types, invalid code lengths, bad distance references, checksum mismatches, and length mismatches. Lack of progress or `Z_FINISH` without completion yields `Z_BUF_ERROR`.

## Dependencies
Uses `zutil.h`, `inftrees.h`, `inflate.h`, and `inffast.h`. It is central to `gzio.c`, `uncompr.c`, and other zlib consumers in this Ghostscript tree.
