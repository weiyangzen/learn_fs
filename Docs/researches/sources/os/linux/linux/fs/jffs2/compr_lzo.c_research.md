# File Research: sources/os/linux/linux/fs/jffs2/compr_lzo.c

This file implements the LZO compressor plugin. It allocates global LZO compression workspace with `vmalloc()` and serializes compression with `deflate_mutex` because `lzo_mem` and `lzo_compress_buf` are shared.

`alloc_workspace()` creates `lzo_mem` sized by `LZO1X_MEM_COMPRESS` and a worst-case PAGE_SIZE compression buffer. `free_workspace()` releases both.

`jffs2_lzo_compress()` compresses `*sourcelen` bytes into the shared temporary buffer, fails if the LZO call fails or if the compressed result exceeds caller-provided `*dstlen`, copies the compressed data to `cpage_out`, and updates `*dstlen`. It does not alter `*sourcelen` on success.

`jffs2_lzo_decompress()` uses `lzo1x_decompress_safe()` and requires the decompressed byte count to equal `destlen`, otherwise returning failure.

The static compressor descriptor registers as `JFFS2_COMPR_LZO`, priority `JFFS2_LZO_PRIORITY`, enabled by default. Init allocates the workspace before registry insertion; exit unregisters and frees workspace.

Key dependencies: kernel LZO API, `compr.h`, and the generic compressor registry.
