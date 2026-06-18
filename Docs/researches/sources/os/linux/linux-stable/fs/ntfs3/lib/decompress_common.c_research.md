# File Research: sources/os/linux/linux-stable/fs/ntfs3/lib/decompress_common.c

## Role

Shared Huffman-table construction for NTFS3 XPRESS and LZX decompressors.

## Key Function

- `make_huffman_decode_table()` builds a fast decode table for canonical prefix codes.
  - Counts codeword lengths.
  - Rejects over-subscribed and incomplete prefix codes, except the fully empty code case allowed by LZX/XPRESS.
  - Sorts symbols by length and symbol value.
  - Fills direct lookup entries for codewords up to `table_bits`.
  - Builds compact binary-tree entries for longer codewords.
  - Encodes fast-path entries as symbol plus codeword length and internal nodes with high marker bits.

## Inputs and Constraints

- `num_syms` is limited by callers to small fixed alphabets.
- `table_bits` controls direct lookup table size.
- `max_codeword_len` bounds accepted lengths.
- `working_space` supplies length counts, offsets, and sorted symbols.

## Research Notes

This is format-agnostic canonical-code infrastructure. The table layout is tuned for the `read_huffsym()` helper in the companion header, where short codewords decode in one table lookup and long codewords traverse a small tree.
