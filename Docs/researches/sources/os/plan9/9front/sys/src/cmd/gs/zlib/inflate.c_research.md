# File Research: sources/os/plan9/9front/sys/src/cmd/gs/zlib/inflate.c

## Purpose
Implements zlib decompression for zlib-wrapped, raw deflate, and optionally gzip-wrapped streams.

## Key Elements
Exports `inflateReset`, `inflateInit2_`, `inflateInit_`, `inflate`, `inflateEnd`, `inflateSetDictionary`, `inflateSync`, `inflateSyncPoint`, and `inflateCopy`. The main `inflate()` routine is a resumable state machine covering wrapper headers, optional dictionaries, stored blocks, fixed blocks, dynamic Huffman blocks, trailer checks, and sync recovery.

## Behavior/Risks
`windowBits` controls raw/zlib/gzip behavior. The sliding window is lazily allocated through `updatewindow()`. `inflate()` updates Adler-32 for zlib streams and CRC32 for gzip streams, validates gzip length trailers, and uses `inflate_fast()` when buffers are large enough. `flush` mostly influences return status; decompression still tries to consume/produce as much as possible. Error states are sticky until reset. `inflateCopy` deep-copies state and adjusts internal table pointers into the copied `codes` array.

## Dependencies
Includes `zutil.h`, `inftrees.h`, `inflate.h`, and `inffast.h`; optionally includes `inffixed.h`. Depends on checksum routines, zlib memory allocation hooks, and Huffman table generation.
