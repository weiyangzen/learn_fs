# File Research: sources/os/plan9/9front/sys/src/cmd/gs/zlib/gzio.c

## Purpose
Implements zlib’s `gz*` stdio-style API for reading and writing gzip streams.

## Key Elements
Defines internal `gz_stream` state and implements `gzopen`, `gzdopen`, `gzread`, `gzwrite`, `gzprintf`, `gzseek`, `gzrewind`, `gztell`, `gzeof`, `gzclose`, `gzerror`, and `gzclearerr`. It parses gzip headers, writes simple gzip headers, maintains CRC32, handles trailers, and supports transparent reads for non-gzip inputs.

## Behavior/Risks
Reading uses raw inflate with `-MAX_WBITS` after manually consuming the gzip header. Concatenated gzip members are detected by checking the next header after trailer validation. Seeking in compressed input is emulated by rewinding/skipping uncompressed bytes and can be very slow. Write-mode seeking fills gaps by writing zero bytes. `gzprintf` is bounded by `Z_PRINTF_BUFSIZE`; old non-ANSI paths depend on `sprintf`/`snprintf` availability macros. Header parsing sets `transparent` when gzip magic is absent.

## Dependencies
Includes `zutil.h`, uses zlib inflate/deflate, `crc32`, stdio file I/O, allocation through local `malloc` wrappers, and portability macros from zlib configuration headers.
