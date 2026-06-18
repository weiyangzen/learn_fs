# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/huffman.h

This header defines the data structures used by Layer III Huffman decoding. `struct huffquad` stores either an intermediate pointer (`bits`, `offset`) or a final quadruple value (`v`, `w`, `x`, `y`, `hlen`). `struct huffpair` is the equivalent for decoded pair values (`x`, `y`, `hlen`). Each entry has a `final` byte indicating whether the lookup is terminal.

`struct hufftable` wraps a pair table pointer with the table's `linbits` and `startbits`, allowing Layer III code to select the correct lookup behavior for each MPEG Huffman table number. The header exports `mad_huff_quad_table` and `mad_huff_pair_table`, both defined in `huffman.c`.

This header has no functions; it is a compact ABI between table data and `layer3.c`'s `III_huffdecode`. The design favors fast table-driven decoding over bit-by-bit tree traversal.
