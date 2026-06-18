# File Research: sources/local-fs/linux-apfs-rw/libzbitmap.h

## Purpose
Declares the APFS LZBITMAP/ZBM decompression API used by the compression subsystem.

## API
- `zbm_decompress(void *dest, size_t dest_size, const void *src, size_t src_size, size_t *out_len)`: decompresses an LZBITMAP buffer or, with `dest == NULL`, computes the expected decompressed length.

## Dependencies
Includes Linux `errno` and `types` headers.

## Notes
The header documents the dual GPL-2.0+/MIT licensing inherited from the Corellium port and upstream `libzbitmap`.
