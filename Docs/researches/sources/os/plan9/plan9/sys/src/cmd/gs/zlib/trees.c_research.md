# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/trees.c

## Purpose
Implements deflate-side Huffman tree generation and compressed block emission. It turns literal/match tallies from the deflater into stored, static-Huffman, or dynamic-Huffman deflate blocks.

## Main Exported/Internal API
Exports zlib-internal tree routines:
- `_tr_init`
- `_tr_stored_block`
- `_tr_align`
- `_tr_flush_block`
- `_tr_tally`

Internal helpers include:
- `tr_static_init`
- `init_block`
- `pqdownheap`
- `gen_bitlen`
- `gen_codes`
- `build_tree`
- `scan_tree`
- `send_tree`
- `build_bl_tree`
- `send_all_trees`
- `compress_block`
- `set_data_type`
- `bi_reverse`
- `bi_flush`
- `bi_windup`
- `copy_block`

## Static Data
Defines or includes:
- Extra-bit tables for lengths, distances, and bit-length codes.
- Bit-length-code send order.
- Static literal and distance trees.
- Distance-code and length-code lookup tables.
- Base length and distance tables.

When `GEN_TREES_H` is defined, it can regenerate `trees.h`.

## Algorithm
`_tr_tally()` records literals or length/distance matches and increments tree frequencies. `_tr_flush_block()` then:
1. Builds literal and distance Huffman trees when compression is enabled.
2. Builds the bit-length tree used to describe those trees.
3. Estimates stored/static/dynamic block sizes.
4. Emits the cheapest legal encoding, unless forced by compile-time options.
5. Resets per-block tallies and aligns the bit buffer on EOF.

Dynamic tree construction uses a heap ordered by frequency with depth tie-breaking. `gen_bitlen()` corrects bit-length overflow to satisfy max code lengths. `gen_codes()` assigns canonical bit-reversed deflate codes.

## Bit Output
`send_bits`, `put_short`, `bi_flush`, and `bi_windup` manage the deflate bitstream in LSB-first order. Stored blocks are byte-aligned and include length plus one’s complement.

## Data Type Guessing
`set_data_type()` marks the stream as ASCII or binary using a simple frequency heuristic over literal bytes.

## Dependencies
Includes `deflate.h` and relies on deflate-state buffers such as `pending_buf`, `dyn_ltree`, `dyn_dtree`, `bl_tree`, `l_buf`, and `d_buf`.
