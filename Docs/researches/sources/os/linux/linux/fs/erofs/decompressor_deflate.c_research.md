# File Research: sources/os/linux/linux/fs/erofs/decompressor_deflate.c

Implements EROFS DEFLATE decompression.

Key behavior:
- Maintains a global pool of zlib inflate streams sized by `deflate_streams` or possible CPUs.
- Lazily allocates zlib workspaces when DEFLATE config is loaded.
- Validates DEFLATE config and windowbits.
- Decompression obtains exact input size, waits for an available stream, initializes raw inflate, and streams through `z_erofs_stream_switch_bufs()`.
- Uses a per-stream bounce page and forces `fillgaps` because DEFLATE cannot write to NULL output buffers.
- Returns stream contexts to the pool and wakes waiters.
- Optionally attempts crypto-accelerated DEFLATE first for non-partial requests.

Important interactions:
- Registered as `z_erofs_deflate_decomp`.
- Uses common streaming and padding helpers from `decompressor.c`.
