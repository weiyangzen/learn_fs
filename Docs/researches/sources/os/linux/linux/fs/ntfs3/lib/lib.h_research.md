# File Research: sources/os/linux/linux/fs/ntfs3/lib/lib.h

## Role

Public internal header for NTFS3 decompressor allocation, freeing, and decompression entry points.

## API Surface

- XPRESS:
  - `xpress_allocate_decompressor()`
  - `xpress_free_decompressor()`
  - `xpress_decompress()`
- LZX:
  - `lzx_allocate_decompressor()`
  - `lzx_free_decompressor()`
  - `lzx_decompress()`

## Dependencies

Includes `<linux/types.h>` and forward-declares `struct xpress_decompressor` and `struct lzx_decompressor`.

## Research Notes

This header intentionally hides decompressor internals. NTFS3 callers only manage opaque decompressor workspaces and call the selected format-specific decompression function.
