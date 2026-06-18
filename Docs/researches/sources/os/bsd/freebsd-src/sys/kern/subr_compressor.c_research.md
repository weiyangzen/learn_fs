# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_compressor.c

## Purpose
Provides a small pluggable compressor interface used for compressed user and kernel core dumps.

## Main Elements
- Framework:
  - `struct compressor_methods`: format, init, reset, write, fini methods.
  - `struct compressor`: selected methods, private stream, output callback, and callback argument.
  - `DATA_SET(compressors, ...)` registers built-in formats.
  - `compressor_avail()`, `compressor_init()`, `compressor_format()`, `compressor_reset()`, `compressor_write()`, `compressor_flush()`, `compressor_fini()`.
- Gzip backend under `GZIO`:
  - `gz_stream` stores output buffer, offset, CRC, and zlib state.
  - `gz_init()` clamps compression level and initializes raw deflate.
  - `gz_reset()` emits a gzip header into the output buffer.
  - `gz_write()` streams input, updates CRC, flushes full buffers via callback, and appends gzip trailer on finish.
  - `gz_fini()` ends zlib and frees buffers.
- Zstd backend under `ZSTDIO`:
  - `zstdio_stream` stores static zstd context, input/output buffers, offset, and workspace.
  - `zstdio_init()` allocates M_NODUMP workspace and buffer, enables checksum, and sets compression level.
  - `zstdio_reset()` resets the zstd session and unknown source size.
  - `zst_flush_intermediate()` writes full output blocks, bounded by `maxiosize`.
  - `zstdio_flush()` finalizes the stream and writes remaining partial output.
  - `zstdio_write()` streams data and detects lack of forward progress.
  - `zstdio_fini()` frees workspace, buffer, and stream.

## Dependencies And Integration
Uses compile-time options `opt_gzio.h` and `opt_zstdio.h`, zlib, zstd, linker sets, kernel malloc, endian helpers, and `M_NODUMP` to avoid including compressor state in dumps being compressed.

## Risk Notes
The callback is the only output path, so errors must propagate immediately. Gzip manually constructs headers/trailers and tracks stream offset and CRC. Zstd protects against no-forward-progress loops and emits full blocks before final partial output. `compressor_fini()` calls the backend finalizer for private state; callers must follow the surrounding API contract for the wrapper object lifetime.
