# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/deflate.h

## Purpose
Defines internal data structures, constants, macros, and tree-function interfaces used by zlib deflate compression.

## Public Surface
Internal-only header, not for applications. Key definitions:
- Compression code constants: `LENGTH_CODES`, `LITERALS`, `L_CODES`, `D_CODES`, `BL_CODES`, `MAX_BITS`.
- Stream statuses: `INIT_STATE`, `BUSY_STATE`, `FINISH_STATE`.
- Types: `ct_data`, `tree_desc`, `Pos`, `IPos`, `deflate_state`.
- Macros: `put_byte`, `MIN_LOOKAHEAD`, `MAX_DIST`, `d_code`, `_tr_tally_lit`, `_tr_tally_dist`.
- Tree-function declarations: `_tr_init`, `_tr_tally`, `_tr_flush_block`, `_tr_align`, `_tr_stored_block`.

## Implementation Notes
- Enables gzip support unless `NO_GZIP` is defined.
- `deflate_state` contains stream backlink, pending output, wrapper state, LZ77 window/hash state, match parameters, Huffman trees, buffers, and bit output state.
- `pending_buf` is shared with literal/distance buffer layout by `deflate.c`.
- Inline tally macros update literal/distance buffers and dynamic tree frequencies unless `DEBUG` is enabled.

## Dependencies
Includes `zutil.h` and assumes tree code provides length/distance code tables.

## Risks and Notes
- State layout is tightly coupled to `deflate.c` and `trees.c`.
- Buffer sizing assumptions are documented and affect compression correctness/performance.
- Filesystem relevance: none.
