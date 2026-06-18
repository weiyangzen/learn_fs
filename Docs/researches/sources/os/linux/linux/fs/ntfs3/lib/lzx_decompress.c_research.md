# File Research: sources/os/linux/linux/fs/ntfs3/lib/lzx_decompress.c

## Role

LZX decompressor used for NTFS “System Compressed” files. It is based on wimlib-derived code and supports the 32768-byte window size used by system compression.

## Format Constants and State

- Supports LZX block types: verbatim, aligned-offset, and uncompressed.
- Uses 256 literal symbols, match lengths 2-257, 30 offset slots, recent-offset queue of 3, and default block size 32768.
- Defines decode table sizes for main, length, precode, and aligned-offset Huffman codes.
- `struct lzx_decompressor` stores all decode tables, codeword-length arrays, and Huffman table working space.

## Main Flow

- `lzx_allocate_decompressor()` allocates reusable workspace.
- `lzx_decompress()` initializes the input bitstream, clears delta-encoded length arrays, loops over blocks until the output buffer is full, and postprocesses x86 E8 translations when needed.
- `lzx_free_decompressor()` frees workspace.

## Block Handling

- `lzx_read_block_header()` reads block type and size.
- For aligned blocks, it reads and builds the aligned offset code.
- For verbatim/aligned compressed blocks, it reads main-code and length-code codeword lengths through the precode and builds decode tables.
- For uncompressed blocks, it aligns the stream, reads recent offsets, and rejects zero offsets.

## Symbol and Match Decoding

- `lzx_read_codeword_lens()` decodes delta-coded Huffman lengths using a precode and handles run-length symbols 17, 18, and 19.
- `lzx_decompress_block()` decodes literals and matches, handles recent offsets and explicit offset slots, reads aligned-offset low bits when applicable, validates match length/offset against output bounds, and copies matches with `lz_copy()`.

## E8 Postprocessing

- `undo_e8_translation()` and `lzx_postprocess()` reverse LZX x86 CALL preprocessing using the default 12,000,000-byte file-size convention.
- Postprocessing is skipped when the decoded data cannot contain E8 literals.

## Dependencies

Uses `decompress_common.h` for bitstream, Huffman, and LZ-copy helpers and `lib.h` for exported prototypes.

## Research Notes

The implementation is intentionally narrow: it targets the LZX variant needed by NTFS WOF/System Compression rather than a general cabinet-file LZX decoder. Bounds checks before `lz_copy()` are the primary protection against malformed compressed streams.
