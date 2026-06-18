# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_deflate.h

Internal deflate compressor state header for the HAMMER2-local zlib copy.

Key responsibilities:
- Defines deflate coding constants for literal/length codes, distance codes, bit-length codes, heap size, max Huffman bits, and bit-buffer size.
- Defines stream status constants used by the compressor state machine.
- Defines Huffman tree node structures, tree descriptors, position types, and the full `deflate_state` structure.
- Declares tree-output helper functions used by `hammer2_zlib_deflate.c`.
- Defines output, lookahead, distance, and tree-tally helper macros.

Important implementation details:
- `deflate_state` stores the zlib stream pointer, pending output buffer, wrapping/status fields, sliding window, hash chains, match-search state, compression-level tunables, Huffman trees, literal/distance buffers, bit output state, and high-water initialization marker.
- `MIN_LOOKAHEAD`, `MAX_DIST`, and `WIN_INIT` encode assumptions used by match search and window refill code.
- `_tr_tally_lit` and `_tr_tally_dist` are inlined when `H2_ZLIB_DEBUG` is not enabled, updating literal/distance buffers and dynamic tree frequencies directly.
- External `_length_code` and `_dist_code` tables are required for distance/length code mapping.

Dependencies:
- Includes `hammer2_zlib_zutil.h`.
- Used by deflate implementation and tree implementation files in the bundled zlib directory.

Notable risks:
- This is internal zlib ABI; any field layout or macro change must be coordinated with deflate and tree code.
- Buffer overlay assumptions between pending output and literal/distance buffers are made by the implementation and are easy to break.
- Macros such as `_tr_tally_dist` evaluate arguments in specific ways and assume caller-supplied values are already range-adjusted.
