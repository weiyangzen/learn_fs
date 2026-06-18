# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/trees.h

## Purpose
Generated static table header for deflate tree support. It is created by building `trees.c` with `-DGEN_TREES_H`.

## Contents
Defines:
- `static_ltree[L_CODES+2]`: fixed literal/length tree codes and lengths.
- `static_dtree[D_CODES]`: fixed distance tree codes and lengths.
- `_dist_code[DIST_CODE_LEN]`: lookup table mapping normalized distances to distance-code numbers.
- `_length_code[MAX_MATCH-MIN_MATCH+1]`: lookup table mapping normalized match lengths to length-code numbers.
- `base_length[LENGTH_CODES]`: base normalized length per length code.
- `base_dist[D_CODES]`: base normalized distance per distance code.

## Usage
Included by `trees.c` for ANSI C builds instead of generating static tables at runtime. The tables speed deflate block construction and static-Huffman emission.

## Notes
This is generated data, not hand-written logic. Its correctness is tied to `tr_static_init()` and `gen_trees_header()` in `trees.c`.
