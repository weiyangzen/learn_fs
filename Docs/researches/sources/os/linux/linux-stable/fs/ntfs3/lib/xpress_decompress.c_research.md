# File Research: sources/os/linux/linux-stable/fs/ntfs3/lib/xpress_decompress.c

## Role

XPRESS Huffman decompressor for NTFS “System Compressed” files.

## Key Structures and Constants

- `XPRESS_NUM_SYMBOLS` is 512.
- `XPRESS_MAX_CODEWORD_LEN` is 15.
- `XPRESS_MIN_MATCH_LEN` is 3.
- `struct xpress_decompressor` contains one Huffman decode table, symbol-length array, and canonical-table working space.

## Key Functions

- `xpress_allocate_decompressor()` allocates reusable workspace.
- `xpress_decompress()`:
  - Reads 4-bit codeword lengths packed two per byte.
  - Builds the Huffman decode table.
  - Decodes symbols until the output buffer is full.
  - Emits literal bytes for symbols below 256.
  - Decodes match length and logarithmic offset fields for symbols above 255.
  - Handles extended length encodings.
  - Validates offset and length before copying with `lz_copy()`.
- `xpress_free_decompressor()` frees the workspace.

## Error Handling

The decoder returns `-1` for too-short headers, invalid Huffman length sets, match offsets before output start, and match lengths beyond the output buffer.

## Research Notes

XPRESS is smaller and simpler than the LZX path: one Huffman code drives both literals and match descriptors, with the remaining offset/length detail read directly from the bitstream.
