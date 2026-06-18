# File Research: sources/os/linux/linux-stable/fs/squashfs/decompressor.h

## Summary
Defines the per-compression-algorithm operations table used by Squashfs decompressor wrappers.

## Main Contents
- `struct squashfs_decompressor`.
- Inline `squashfs_comp_opts()`.
- Conditional extern declarations for compiled compression backends.

## Important Details
Each backend can provide `init`, `comp_opts`, `free`, and `decompress`. `alloc_buffer` tells the direct page actor whether missing page-cache pages can be handled with a temporary buffer. `supported` distinguishes usable backends from registry stubs.

## Risks
Backend wrappers and thread implementations share this ABI. The `decompress` function receives the algorithm-private stream selected by the thread implementation, not the global `msblk->stream`.
