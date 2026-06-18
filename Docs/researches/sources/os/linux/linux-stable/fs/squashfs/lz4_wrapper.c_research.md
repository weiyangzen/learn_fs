# File Research: sources/os/linux/linux-stable/fs/squashfs/lz4_wrapper.c

## Summary
Implements the Squashfs LZ4 decompressor backend.

## Key APIs
- Exports `squashfs_lz4_comp_ops`.

## Important Behavior
LZ4 filesystems must carry compression options, and the wrapper accepts only the legacy LZ4 format version. Initialization allocates vmalloc input and output buffers sized to the maximum of filesystem block size and metadata block size.

Decompression copies compressed BIO segments into the input buffer, calls `LZ4_decompress_safe()`, then copies decompressed bytes from the output buffer into the page actor.

## Risks
The wrapper does not stream directly from BIO to actor; it depends on full-size input/output buffers. The legacy option validation is required for format compatibility.
