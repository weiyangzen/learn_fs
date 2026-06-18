# File Research: sources/os/linux/linux-stable/fs/ntfs3/lib/lzx_decompress.c

## Role

LZX decompressor for NTFS “System Compressed” files. It supports the 32768-byte window size used by this NTFS compression mode and is based on wimlib-derived logic.

## Key Structures and Constants

- Defines LZX block types: verbatim, aligned offset, and uncompressed.
- Uses fixed symbol counts for literals, length symbols, offset slots, precode symbols, and aligned-offset symbols.
- `struct lzx_decompressor` owns reusable decode tables, codeword-length arrays, and Huffman working space.

## Key Functions

- `lzx_allocate_decompressor()` allocates the reusable workspace.
- `undo_e8_translation()` reverses x86 CALL-target preprocessing for one offset.
- `lzx_postprocess()` scans decompressed data and reverses E8 preprocessing when relevant.
- `read_presym()`, `read_mainsym()`, `read_lensym()`, and `read_alignedsym()` decode symbols from the relevant Huffman table.
- `lzx_read_codeword_lens()` reads precode lengths, builds the precode table, and decodes delta/RLE-encoded codeword lengths.
- `lzx_read_block_header()` reads block type and size, builds main/length/aligned Huffman tables for compressed blocks, and loads recent offsets for uncompressed blocks.
- `lzx_decompress_block()` decodes literals and matches, maintains recent-offset state, handles aligned offsets, validates match bounds, and copies matches via `lz_copy()`.
- `lzx_decompress()` loops over blocks until the requested output buffer is full, handles compressed and uncompressed blocks, and runs E8 postprocessing if possible.
- `lzx_free_decompressor()` frees the workspace.

## Error Handling

Invalid block types, impossible block sizes, invalid Huffman tables, zero recent offsets, input exhaustion, match underruns, and output overruns all return `-1`.

## Research Notes

The implementation is intentionally constrained to the NTFS/WIM-style LZX profile rather than general cabinet-file LZX. Recent-offset handling and E8 postprocessing are essential compatibility details for Windows system-compressed data.
