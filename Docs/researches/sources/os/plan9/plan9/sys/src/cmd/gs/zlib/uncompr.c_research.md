# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/uncompr.c

## Purpose
Implements zlib’s one-shot `uncompress()` helper for decompressing a complete memory buffer into a caller-provided destination buffer.

## API
```c
int uncompress(Bytef *dest,
               uLongf *destLen,
               const Bytef *source,
               uLong sourceLen);
```

## Behavior
Initializes a local `z_stream`, checks that source and destination sizes fit in `uInt`, calls `inflateInit`, then calls `inflate(..., Z_FINISH)` once. On success, it stores `stream.total_out` in `*destLen` and ends the stream.

## Error Mapping
If inflate does not end with `Z_STREAM_END`, the function cleans up and maps `Z_NEED_DICT` or an exhausted-input `Z_BUF_ERROR` to `Z_DATA_ERROR`. Other inflate errors are returned directly.

## Use Case
Useful when the caller already knows the full uncompressed size and has a sufficiently large destination buffer, such as decompressing an mmap’d file or in-memory resource.
