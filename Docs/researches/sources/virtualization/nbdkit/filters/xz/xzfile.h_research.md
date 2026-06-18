# File Research: sources/virtualization/nbdkit/filters/xz/xzfile.h

This header declares the opaque `xzfile` helper used by `xz.c`. It exposes lifecycle functions, metadata accessors, and block decompression.

`xzfile_open(nbdkit_next *)` verifies and parses the underlying xz stream indexes. `xzfile_close` releases liblzma index resources. `xzfile_max_uncompressed_block_size` returns the largest block size for configuration enforcement, while `xzfile_get_size` returns total uncompressed size.

`xzfile_read_block` decompresses the block containing a requested uncompressed offset and returns a heap buffer owned by the caller, along with block start and size. Its interface deliberately works at xz block granularity so `xz.c` can cache decompressed blocks.
