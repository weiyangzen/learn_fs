# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/gzio.c

## Purpose
Implements zlib’s `gz*` file API for reading and writing gzip streams through stdio. It wraps raw deflate/inflate streams with gzip header/trailer handling, CRC maintenance, transparent passthrough for non-gzip input, and limited uncompressed-position seeking.

## Main API Surface
Exports:
- `gzopen(path, mode)` and `gzdopen(fd, mode)` for path/file-descriptor backed gzip streams.
- `gzread`, `gzgetc`, `gzungetc`, `gzgets` for reads.
- `gzwrite`, `gzprintf`, `gzputc`, `gzputs`, `gzflush` for writes when compression is enabled.
- `gzseek`, `gzrewind`, `gztell`, `gzeof`, `gzclose`, `gzerror`, `gzclearerr`.
- Internal helpers include `gz_open`, `get_byte`, `check_header`, `destroy`, `putLong`, `getLong`, and `do_flush`.

## Internal State
`gz_stream` owns:
- Embedded `z_stream`.
- Input/output buffers sized by `Z_BUFSIZE`.
- `FILE *file`, path/debug string, mode, transparent flag, gzip CRC, byte counters, and one-byte pushback state.
- `start`, `in`, and `out` offsets for compressed-data start and logical byte positions.

## Behavior
Read mode initializes raw inflate via `inflateInit2(..., -MAX_WBITS)` and then parses gzip headers manually. If the magic header is absent, the stream becomes transparent and `gzread` copies bytes without decompression. For gzip members, `gzread` verifies CRC32 and consumes the stored original length, then detects concatenated gzip members and resets inflate for the next member.

Write mode initializes raw deflate and emits a minimal 10-byte gzip header. `gzclose` finishes deflate, emits CRC32 and uncompressed input size in little-endian order, then releases all state.

`gzseek` on read streams is replay-based: backward seeks rewind and re-decompress forward, while forward seeks read and discard output. On write streams, seeking forward writes zero bytes.

## Error Handling and Risks
Errors are tracked in `s->z_err` and exposed through `gzerror`. Filesystem errors use `Z_ERRNO` and `errno`. `gzprintf` protects against formatted-output overflow by checking the fixed-size buffer and terminating byte, but non-ANSI fallback paths depend on `snprintf` availability macros. `gzdopen` does not duplicate the descriptor, matching `fdopen` behavior.

## Dependencies
Depends on `zutil.h`, deflate/inflate APIs, CRC32, stdio, allocation helpers, and zlib portability macros. It is a user-space compression file wrapper, not a Plan 9 kernel/VFS implementation.
