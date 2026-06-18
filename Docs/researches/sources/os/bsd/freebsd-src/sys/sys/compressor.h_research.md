# File Research: sources/os/bsd/freebsd-src/sys/sys/compressor.h

## Purpose
Declares the kernel compression stream abstraction used by crash dump and related kernel-output paths.

## Main Elements
- Supported formats: `COMPRESS_GZIP` and `COMPRESS_ZSTD`.
- `compressor_cb_t` callback writes compressed chunks with size and offset.
- Opaque `struct compressor` lifecycle: `compressor_init()`, `compressor_reset()`, `compressor_flush()`, `compressor_fini()`.
- Streaming API: `compressor_write()`, `compressor_format()`, `compressor_avail()`.

## Dependencies And Integration
Kernel-only header. Used by kernel dump code and other in-kernel compression consumers.

## Risk Notes
The callback contract is central: write ordering, max I/O size, and flush/fini behavior must be honored by callers to avoid corrupt compressed output.
