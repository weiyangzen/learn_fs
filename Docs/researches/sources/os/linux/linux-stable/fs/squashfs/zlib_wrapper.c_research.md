# File Research: sources/os/linux/linux-stable/fs/squashfs/zlib_wrapper.c

## Summary
Implements the Squashfs zlib decompressor backend.

## Key APIs
- Exports `squashfs_zlib_comp_ops`.

## Important Behavior
Initialization allocates a `z_stream` and vmalloc zlib inflate workspace. Decompression lazily calls `zlib_inflateInit()`, feeds BIO segments as input, writes output through the page actor, and calls `zlib_inflateEnd()` before returning `total_out`.

`alloc_buffer = 1`, enabling temporary direct-actor output for missing page-cache pages.

## Risks
The wrapper must reach `Z_STREAM_END`; otherwise it reports `-EIO`. The inflate stream state is reused by the selected decompressor thread implementation, so callers must serialize per-stream use.
