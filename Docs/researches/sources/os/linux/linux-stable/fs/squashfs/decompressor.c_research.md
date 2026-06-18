# File Research: sources/os/linux/linux-stable/fs/squashfs/decompressor.c

## Summary
Implements the Squashfs decompressor registry and decompressor setup path.

## Key APIs
- `squashfs_lookup_decompressor()`.
- `squashfs_decompressor_setup()`.

## Important Behavior
The registry always contains entries for zlib, lz4, lzo, xz, lzma, zstd, and unknown compression. Unsupported compiled-out algorithms are represented by stubs with `supported = 0`; lzma is always unsupported.

`get_comp_opts()` reads optional compressor-specific options from immediately after the superblock when the filesystem flags indicate they exist. It passes the raw option block to the selected decompressor's `comp_opts` callback.

`squashfs_decompressor_setup()` obtains compressor options and delegates stream creation to the selected decompressor thread-ops implementation.

## Risks
The raw options block is read through normal Squashfs metadata/block I/O before the main stream exists; this path depends on uncompressed option block handling and early superblock `bytes_used` initialization.
