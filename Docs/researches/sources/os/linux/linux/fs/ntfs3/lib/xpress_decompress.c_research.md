# File Research: sources/os/linux/linux/fs/ntfs3/lib/xpress_decompress.c

## Role

XPRESS Huffman decompressor used for NTFS “System Compressed” files. It is based on wimlib-derived code and shares Huffman/bitstream/LZ primitives with the LZX decompressor.

## Key Definitions

- `XPRESS_NUM_SYMBOLS`: 512.
- `XPRESS_MAX_CODEWORD_LEN`: 15.
- `XPRESS_MIN_MATCH_LEN`: 3.
- `XPRESS_TABLEBITS`: 12.
- `struct xpress_decompressor` stores the decode table, symbol lengths, and Huffman working space.

## Main Flow

- `xpress_allocate_decompressor()` allocates workspace.
- `xpress_decompress()`:
  - reads 512 4-bit codeword lengths from the compressed header;
  - builds a Huffman decode table;
  - decodes symbols until the output buffer is filled;
  - writes literals for symbols below 256;
  - decodes match length and log2 offset from symbols 256+;
  - reads extra offset bits and extended lengths;
  - validates offset and length against output bounds;
  - copies matches with `lz_copy()`.
- `xpress_free_decompressor()` frees workspace.

## Dependencies

Uses `decompress_common.h` and `lib.h`.

## Research Notes

The decompressor returns `-1` for malformed input rather than errno-style Linux negatives. It depends on caller-provided output size being the exact expected uncompressed size.
