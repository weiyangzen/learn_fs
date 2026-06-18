# File Research: sources/os/linux/linux/fs/ntfs3/lib/decompress_common.c

## Role

Shared decompression implementation for NTFS3 XPRESS and LZX decompressors. It builds canonical Huffman/prefix-code decode tables used by both formats.

## Key Function

`make_huffman_decode_table()` takes codeword lengths and creates a fast decode table:

- counts symbols by codeword length;
- validates that the code lengths form a complete prefix code, while allowing an entirely empty code as valid for LZX/XPRESS;
- sorts symbols by canonical code order;
- fills direct lookup table entries for codewords up to `table_bits`;
- builds binary-tree overflow entries for longer codewords;
- stores direct entries as `(length << 11) | symbol`;
- stores internal tree nodes with high bits `0xC000`;
- returns `0` on success and `-1` for invalid lengths.

## Dependencies

Includes `decompress_common.h`, which provides kernel types, unaligned access helpers, bitstream helpers, and shared LZ-copy routines.

## Research Notes

This is format-independent prefix-code infrastructure imported from Eric Biggers’ decompressor code. Validation of over-subscribed or incomplete code length sets is the key safety boundary before XPRESS/LZX symbol decoding.
