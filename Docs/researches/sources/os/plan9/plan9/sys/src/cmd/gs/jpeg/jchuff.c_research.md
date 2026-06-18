# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jchuff.c

Sequential Huffman entropy encoder for JPEG compression.

Key behavior:
- Maintains MCU-local savable state for bit buffering and DC predictions so output suspension can back up to an MCU boundary.
- Expands JPEG Huffman table definitions into fast symbol-to-code/length tables via `jpeg_make_c_derived_tbl`.
- Emits bits with byte stuffing after `0xFF` bytes and supports restart markers.
- Encodes DC coefficient differences and AC run-length/value symbols in JPEG natural-order traversal.
- Provides optional entropy-optimization support by gathering symbol frequencies and building optimal Huffman tables with `jpeg_gen_optimal_table`.
- `jinit_huff_encoder` installs the entropy encoder and initializes derived/statistics table pointers.

Dependencies:
- Shares declarations with `jcphuff.c` through `jchuff.h`.
- Uses destination-manager callbacks, JPEG coefficient ordering, Huffman table arrays, restart state, and memory-manager allocation.

Notable risks:
- Actual output suspension is supported, but marker writing elsewhere is not suspendable.
- Coefficient range checks depend on `MAX_COEF_BITS` from sample precision.
- The optimal-table generator mutates frequency arrays, so callers avoid running it more than once per table.
