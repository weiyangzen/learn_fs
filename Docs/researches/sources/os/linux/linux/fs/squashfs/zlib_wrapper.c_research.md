# File Research: sources/os/linux/linux/fs/squashfs/zlib_wrapper.c

Implements the zlib decompressor wrapper.

Initialization allocates a `z_stream` and vmalloc workspace sized by `zlib_inflate_workspacesize()`. Decompression feeds BIO segments, lazily calls `zlib_inflateInit()`, advances page-actor output buffers, requires `Z_STREAM_END`, and finalizes with `zlib_inflateEnd()`.

Registers compressor id `ZLIB_COMPRESSION`, name `zlib`, supported, with `alloc_buffer = 1`.
