# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/adler32.c

## Purpose
Implements zlib’s Adler-32 checksum function.

## Public Surface
- `uLong ZEXPORT adler32(uLong adler, const Bytef *buf, uInt len)`.

## Implementation Notes
- Splits checksum into `s1` and `s2` modulo 65521.
- Returns initial checksum `1L` when `buf == Z_NULL`.
- Processes input in `NMAX` chunks to avoid 32-bit overflow.
- Uses unrolled macros `DO1` through `DO16` for speed.
- Supports `NO_DIVIDE` builds with repeated subtraction instead of `% BASE`.

## Dependencies
Includes `zlib.h` with `ZLIB_INTERNAL`.

## Risks and Notes
- Correct chunk size is tied to overflow math in the source comment.
- Filesystem relevance: none; checksum primitive.
