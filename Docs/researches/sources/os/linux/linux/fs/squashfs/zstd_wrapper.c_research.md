# File Research: sources/os/linux/linux/fs/squashfs/zstd_wrapper.c

Implements the ZSTD decompressor wrapper.

The workspace stores window size, workspace size, and vmalloc memory. Window size is max(filesystem block size, metadata size), and workspace size comes from `zstd_dstream_workspace_bound()`.

Decompression initializes a zstd dstream from the workspace, streams BIO segments into it, writes output through the page actor, and treats zstd errors or premature page exhaustion as `-EIO`.

Registers compressor id `ZSTD_COMPRESSION`, name `zstd`, supported, with `alloc_buffer = 1`.
