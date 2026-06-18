# File Research: sources/os/linux/linux/fs/jffs2/compr_zlib.c

This file implements the zlib compressor plugin. It uses global `z_stream` instances for deflate and inflate, protected by separate mutexes, and allocates their workspaces with `vmalloc()`.

`alloc_workspaces()` allocates deflate workspace sized by `zlib_deflate_workspacesize(MAX_WBITS, MAX_MEM_LEVEL)` and inflate workspace sized by `zlib_inflate_workspacesize()`. `free_workspaces()` releases both.

`jffs2_zlib_compress()` reserves `STREAM_END_SPACE` bytes for deflate stream termination, initializes zlib with compression level 3, repeatedly calls `zlib_deflate(..., Z_PARTIAL_FLUSH)` while there is input and output room, then finishes with `Z_FINISH`. It fails if zlib errors, the stream does not end cleanly, or output is not smaller than input. It updates `*dstlen` and `*sourcelen` from zlib totals on success.

`jffs2_zlib_decompress()` initializes inflate, with an optimization that skips zlib’s Adler32 verification when the header is a standard deflate stream without a preset dictionary. It inflates until not `Z_OK`, logs non-`Z_STREAM_END`, ends the stream, and returns 0 unless init fails.

The compressor descriptor registers as `JFFS2_COMPR_ZLIB`, priority `JFFS2_ZLIB_PRIORITY`, enabled unless `JFFS2_ZLIB_DISABLED` is defined. Init allocates workspaces then registers; exit unregisters and frees workspaces.

Key dependencies: kernel zlib/zutil APIs, `compr.h`, `nodelist.h`, and the generic compressor registry.
