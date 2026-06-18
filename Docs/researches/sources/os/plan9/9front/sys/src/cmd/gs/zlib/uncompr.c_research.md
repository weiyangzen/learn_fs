# File Research: sources/os/plan9/9front/sys/src/cmd/gs/zlib/uncompr.c

## Purpose
Implements the one-shot `uncompress()` memory-buffer decompression helper.

## Key Elements
Initializes a `z_stream`, points it at caller-provided source and destination buffers, calls `inflateInit`, runs `inflate(..., Z_FINISH)`, stores `stream.total_out` into `*destLen`, and ends the stream.

## Behavior/Risks
Rejects source or destination lengths that cannot fit into `uInt`, which matters on 16-bit targets. If inflate does not reach `Z_STREAM_END`, `Z_NEED_DICT` and a no-input `Z_BUF_ERROR` are normalized to `Z_DATA_ERROR`. Caller must provide a destination buffer large enough for the full uncompressed data.

## Dependencies
Defines `ZLIB_INTERNAL`, includes `zlib.h`, and depends on `inflateInit`, `inflate`, and `inflateEnd`.
