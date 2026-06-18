# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_trees.c

Source read: complete file, 1232 lines.

Purpose: Deflate-side Huffman tree construction and block emission. This file builds static/dynamic literal, distance, and bit-length trees; chooses stored/static/dynamic block encodings; emits compressed block headers and data; and manages bit-buffer output.

Key exported/internal-zlib interfaces:
- `_tr_init(deflate_state *s)` initializes static tables, tree descriptors, bit buffer fields, debug counters, and the first block.
- `_tr_tally(deflate_state *s, unsigned dist, unsigned lc)` records literal or match symbols, updates tree frequencies, and signals when the literal buffer is full enough to flush.
- `_tr_flush_block(deflate_state *s, charf *buf, ulg stored_len, int last)` builds trees, compares stored/static/dynamic sizes, emits the chosen block, resets block state, and winds up bits on the final block.
- `_tr_stored_block()`, `_tr_flush_bits()`, and `_tr_align()` support stored block emission and compressor synchronization.

Implementation notes:
- `tr_static_init()` builds or references the fixed literal and distance trees, length-code map, distance-code map, and base-length/base-distance arrays.
- `build_tree()` uses a heap over frequencies to construct Huffman trees, forces at least two nonzero codes for PKZIP compatibility, computes bit lengths, and generates bit-reversed deflate codes.
- `gen_bitlen()` caps code lengths to maximum widths and redistributes overflowed lengths.
- `scan_tree()` and `send_tree()` encode repeated bit lengths with repeat symbols 16, 17, and 18.
- `build_bl_tree()` constructs the bit-length tree and computes how many bit-length codes need to be transmitted.
- `compress_block()` walks `d_buf`/`l_buf`, emits literal codes or length/distance pairs, includes extra bits, and terminates with end-of-block.
- `detect_data_type()` classifies a block as `Z_TEXT` or `Z_BINARY` from literal frequencies.
- `bi_flush()`, `bi_windup()`, `bi_reverse()`, and `copy_block()` implement low-level bit packing and byte-aligned stored block copying.

Integration:
- Includes `hammer2_zlib_deflate.h`, which defines `deflate_state`, `ct_data`, tree descriptors, buffer helpers, and constants.
- Includes generated `hammer2_zlib_trees.h` unless `GEN_TREES_H` or a non-ANSI compiler path is used.
- Uses `_length_code` and `_dist_code` arrays consumed by both tallying and block compression.

Risks and review notes:
- This file is highly coupled to `deflate_state` buffer layout, especially the overlay assertions involving `pending_buf`, `d_buf`, and `l_buf`.
- Debug code uses `fprintf`, `isgraph`, and debug counters under `H2_ZLIB_DEBUG`; kernel builds should keep debug configuration intentional.
- The generated table path writes `trees.h` through stdio when `GEN_TREES_H` is defined; that should remain a build-time generation mode, not a kernel runtime path.
