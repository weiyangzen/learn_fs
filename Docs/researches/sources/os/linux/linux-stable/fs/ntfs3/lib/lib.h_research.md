# File Research: sources/os/linux/linux-stable/fs/ntfs3/lib/lib.h

## Role

Small public header for NTFS3 system-compression decompressors.

## API Surface

- XPRESS:
  - `xpress_allocate_decompressor()`
  - `xpress_free_decompressor()`
  - `xpress_decompress()`
- LZX:
  - `lzx_allocate_decompressor()`
  - `lzx_free_decompressor()`
  - `lzx_decompress()`

## Research Notes

This header exposes only opaque decompressor handles and one-shot decompression entry points. Implementation details and workspace layouts remain private to the corresponding `.c` files.
