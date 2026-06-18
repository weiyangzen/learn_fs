# File Research: sources/os/linux/linux-stable/fs/squashfs/lzo_wrapper.c

## Summary
Implements the Squashfs LZO decompressor backend.

## Key APIs
- Exports `squashfs_lzo_comp_ops`.

## Important Behavior
Initialization allocates vmalloc input and output buffers sized to the maximum of filesystem block size and metadata block size. Decompression copies compressed BIO data into the input buffer, calls `lzo1x_decompress_safe()`, and copies the resulting output into the page actor.

## Risks
Like LZ4, LZO uses full intermediate buffers and reports all backend failures as `-EIO`. It does not provide a compressor-options parser.
