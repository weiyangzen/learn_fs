# File Research: sources/os/plan9/9front/sys/src/cmd/gs/zlib/trees.c

## Purpose
Implements deflate-side Huffman tree construction and compressed block emission.

## Key Elements
Initializes static trees and length/distance lookup tables, builds dynamic literal/distance/bit-length trees, selects stored/static/dynamic block encoding, emits Huffman-coded block data, tallies literals and matches, and manages the bit output buffer. Key exported internals are `_tr_init`, `_tr_stored_block`, `_tr_align`, `_tr_flush_block`, and `_tr_tally`.

## Behavior/Risks
`_tr_flush_block` compares stored, static, and dynamic costs and emits the cheapest unless forced by compile-time macros. Dynamic tree generation uses heap construction, bit-length limiting, canonical code generation, and run-length encoding of code lengths. Stored blocks are byte-aligned and include length/complement headers. `_tr_tally` flushes when the literal buffer is full. Correctness depends on `deflate_state` buffer layout and pending-buffer capacity assertions.

## Dependencies
Includes `deflate.h` and, for ANSI builds, generated `trees.h`. Uses constants/macros from deflate internals such as `L_CODES`, `D_CODES`, `BL_CODES`, `MAX_BITS`, `put_byte`, and `d_code`.
