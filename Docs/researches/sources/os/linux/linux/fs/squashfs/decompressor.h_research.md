# File Research: sources/os/linux/linux/fs/squashfs/decompressor.h

Declares `struct squashfs_decompressor`, the common interface implemented by all compression wrappers.

The interface includes optional init, compressor-option parsing, free, and decompress callbacks, plus compression id, name, `alloc_buffer`, and `supported` flags.

`alloc_buffer` matters for direct page-cache decompression: streaming wrappers such as zlib/xz/zstd can request temporary buffers for missing pages.

The header also conditionally declares enabled compressor operation tables.
