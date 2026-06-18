# File Research: sources/os/linux/linux/fs/erofs/decompressor_zstd.c

Implements EROFS Zstandard decompression.

Key behavior:
- Maintains a global pool of ZSTD stream contexts sized by `zstd_streams` or possible CPUs.
- Validates ZSTD config and window log.
- Resizes all stream workspaces when a larger dictionary/window is required.
- Isolates stream lists under spinlock and waits when no stream is available.
- Decompression fixes exact input size, initializes a ZSTD dstream, uses common stream switching, and detects corrupted or truncated streams.
- Forces `fillgaps` because ZSTD requires real output buffers.
- Frees workspaces and contexts on exit.

Important interactions:
- Registered as `z_erofs_zstd_decomp`.
- Uses `zstd_dstream_workspace_bound()` and kernel ZSTD streaming APIs.
