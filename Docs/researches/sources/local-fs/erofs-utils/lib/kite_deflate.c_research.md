# File Research: sources/local-fs/erofs-utils/lib/kite_deflate.c

This file implements a custom raw DEFLATE encoder named `kite_deflate`. It includes bit emission, fixed/dynamic Huffman generation, block cost selection, a hash-chain LZ matchfinder, and optional test code that validates output through zlib when available.

Core structures:
- `struct kite_deflate_symbol`: literal or match symbol.
- `struct kite_deflate_table`: Huffman code/length tables for literal/length, distance, and code-length alphabets.
- `struct kite_deflate`: encoder state, buffers, bit writer state, frequencies, selected mode, symbol queue, and matchfinder.
- `struct kite_matchfinder`: hash/chain tables, current offset, cyclic window, match limits, and lazy-match state.

Compression flow:
- `kite_deflate_init_once()` initializes fixed Huffman tables, length slot lookup, and distance fast-position table.
- `kite_deflate_init()` allocates the encoder, symbol array, and matchfinder; level 1-9 config controls lazy search and depth.
- `kite_deflate_destsize()` compresses as much source as fits in a target destination size, updates `*srcsize` to consumed bytes, and returns output bytes.
- `kite_deflate_end()` releases hash/chain/symbol memory.

Block handling:
- `kite_deflate_startblock()` resets frequencies and starts with fixed Huffman mode.
- `deflate_count_code()` updates symbol frequencies and estimated bit costs, switching/recomputing dynamic tables when needed.
- `kite_deflate_endblock()` compares fixed/dynamic/stored block cost and may force final block if remaining output space is tight.
- `kite_deflate_commitblock()` writes fixed, dynamic, or stored blocks.
- `kite_deflate_writeblock()` writes literal and length/distance symbols and the end-of-block marker.
- `kite_deflate_sendtrees()` emits dynamic Huffman tree metadata.

Matchfinding:
- `kite_mf_getmatches_hc3()` hashes 3-byte prefixes using a CRC-CCITT table and searches a bounded hash chain.
- `kite_deflate_fast()` uses immediate longest matches.
- `kite_deflate_slow()` implements lazy matching.
- Level configuration mirrors zlib-style good/lazy/nice/depth values.

Built-in test support:
- Under `TEST`, the file can run a minimal fixed-Huffman test and file compression test.
- With zlib enabled, it inflates generated raw deflate and compares to the original input.

Risks / notes:
- The encoder writes into caller-provided buffers and relies on cost checks plus `DBG_BUGON` to avoid overflow; changes to cost accounting are high risk.
- Static global initialization is guarded by checking `kstaticHuff_distCodes[31]`, not by a lock; concurrent first-use would be worth reviewing if used from multiple threads.
