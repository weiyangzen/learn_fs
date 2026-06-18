# File Research: sources/os/linux/linux-stable/fs/squashfs/zstd_wrapper.c

## Summary
Implements the Squashfs Zstandard decompressor backend.

## Key APIs
- Exports `squashfs_zstd_comp_ops`.

## Important Behavior
Initialization allocates a workspace sized by `zstd_dstream_workspace_bound()` for a window of max(filesystem block size, metadata block size). Decompression initializes a zstd stream from that workspace, feeds BIO segments through `zstd_decompress_stream()`, and emits output through the page actor.

`alloc_buffer = 1`, so direct page-cache reads can tolerate missing page targets through temporary output buffers.

## Risks
The wrapper treats zstd stream errors and unexpected lack of output pages as `-EIO`. Workspace sizing depends on the image block size accepted at mount time.
