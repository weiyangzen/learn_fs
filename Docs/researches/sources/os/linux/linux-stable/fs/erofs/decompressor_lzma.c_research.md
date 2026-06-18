# File Research: sources/os/linux/linux-stable/fs/erofs/decompressor_lzma.c

## Summary
Implements EROFS microLZMA decompression with a pooled set of decoder contexts.

## Main Responsibilities
- Allocates LZMA stream records at init.
- Validates LZMA config records and dictionary size.
- Resizes all stream decoder states when a larger dictionary is needed.
- Streams compressed input and decompressed output across pages.

## Key APIs
- `z_erofs_lzma_decomp`

## Important Behavior
The config path isolates all available stream records before replacing decoder states, then returns them to the global pool. Decompression waits for a stream, runs `xz_dec_microlzma_run()`, and returns the stream.

## Risks
Dictionary resizing and active stream pooling require careful locking and waitqueue coordination. Unsupported format or dictionary sizes fail configuration.
