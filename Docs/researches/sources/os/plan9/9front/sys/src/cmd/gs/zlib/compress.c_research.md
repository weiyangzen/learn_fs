# File Research: sources/os/plan9/9front/sys/src/cmd/gs/zlib/compress.c

## Purpose
Implements zlib’s convenience buffer compression APIs.

## Key Elements
Defines `compress2()`, `compress()`, and `compressBound()`.

## Behavior/Risks
`compress2` wraps `deflateInit`, `deflate(..., Z_FINISH)`, and `deflateEnd` around caller-provided buffers. It checks 16-bit `MAXSEG_64K` truncation and output buffer size truncation. If deflate does not reach stream end, it maps a continuing `Z_OK` to `Z_BUF_ERROR`. `compressBound` returns the classic zlib upper-bound formula for default settings.

## Dependencies
Uses public zlib stream API from `zlib.h`.
