# File Research: sources/os/linux/linux/fs/erofs/decompressor_lzma.c

Implements EROFS microLZMA decompression.

Key behavior:
- Maintains a global stream pool sized by `lzma_streams` or possible CPUs.
- Validates LZMA config format and dictionary size.
- Resizes all stream decoder states when a larger dictionary is required, isolating the stream list to avoid races.
- Decompression fixes exact input size, obtains an available stream, resets the microLZMA decoder, and streams input/output buffers with overlap protection.
- Uses per-stream bounce buffers and returns stream contexts to the pool after each request.
- Cleans up decoder states on exit.

Important interactions:
- Registered as `z_erofs_lzma_decomp`.
- Uses kernel XZ microLZMA decoder and common EROFS stream switching.
