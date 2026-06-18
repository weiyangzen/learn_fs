# File Research: sources/os/linux/linux-stable/fs/squashfs/decompressor_single.c

## Summary
Implements the single-stream decompressor threading mode.

## Key APIs
- Exports `squashfs_decompressor_single`.

## Important Behavior
Mount setup creates one backend decompressor stream and frees compressor options after initialization. Every decompression takes a mutex around the shared stream, so only one block can be decompressed at a time.

`max_decompressors()` returns 1.

## Risks
This mode is memory efficient but serializes metadata, fragment, and file-data decompression across the filesystem instance.
