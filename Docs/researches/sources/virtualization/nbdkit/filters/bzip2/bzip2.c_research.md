# File Research: sources/virtualization/nbdkit/filters/bzip2/bzip2.c

Purpose: exposes a bzip2-compressed backend as a read-only uncompressed NBD export.

Key details:
- Opens the underlying plugin read-only regardless of requested mode.
- On first `.prepare`, protected by a mutex, fully decompresses the backend into an unlinked temporary file.
- Uses `BZ2_bzDecompressInit`, streaming 4 MiB input/output buffers, and records compressed and uncompressed sizes.
- `bzip2_get_size` returns the decompressed size and rejects use if the backend compressed size changes after decompression.
- `.pread` services reads from the temporary uncompressed file with full retry-on-short-read behavior.
- Forces `can_write = 0`, `can_multi_conn = 1`, `can_extents = 0`, and `can_cache = NBDKIT_CACHE_EMULATE`.
- Export description is prefixed with “expansion of bzip2-compressed image”.
- `.unload` closes the temporary file descriptor.

Risk notes:
- Entire image is decompressed before serving size/read data; startup latency and temporary storage requirements scale with decompressed size.
- The bzip2 format lacks embedded uncompressed size, explaining the eager full decompression.
