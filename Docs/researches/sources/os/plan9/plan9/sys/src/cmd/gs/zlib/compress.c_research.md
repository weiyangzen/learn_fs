# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/compress.c

## Purpose
Provides simple one-shot memory-buffer compression wrappers around the streaming deflate API.

## Public Surface
- `compress2(dest, destLen, source, sourceLen, level)`.
- `compress(dest, destLen, source, sourceLen)`.
- `compressBound(sourceLen)`.

## Implementation Notes
- Initializes a `z_stream` with default allocators, input/output buffers, and requested level.
- Calls `deflateInit`, then `deflate(..., Z_FINISH)`, then `deflateEnd`.
- Converts unfinished `Z_OK` from `deflate` into `Z_BUF_ERROR` when output space is insufficient.
- `compress` delegates to `compress2` with `Z_DEFAULT_COMPRESSION`.
- `compressBound` returns the zlib 1.2.2 bound formula for default deflate settings.

## Dependencies
Depends on public zlib API declarations in `zlib.h` and deflate implementation.

## Risks and Notes
- Caller must provide enough output buffer; no dynamic allocation for destination occurs here.
- `compressBound` must stay in sync with default deflate window/memory settings.
- Filesystem relevance: none.
