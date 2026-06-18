# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_deflate.c

HAMMER2-local zlib deflate compressor implementation, adapted from zlib 1.2.8 for kernel allocation and HAMMER2 build integration.

Key responsibilities:
- Implements `deflateInit_()`, `deflateInit2_()`, `deflateResetKeep()`, `deflateReset()`, `deflate()`, and `deflateEnd()`.
- Allocates and initializes compressor state, sliding window, hash chains, and pending/literal/distance buffers.
- Writes zlib headers/trailers, tracks Adler-32, flushes pending output, and manages stream status transitions.
- Implements input reading into the LZ77 window and rolling hash-table maintenance.
- Implements longest-match search, lazy-match compression, RLE strategy, and Huffman-only strategy.
- Flushes completed blocks through tree-building/output helpers declared in the deflate header.

Important implementation details:
- Uses DragonFly kernel `kmalloc`/`kfree` with `C_ZLIB_BUFFER_DEFLATE` instead of userland zlib allocation callbacks.
- All configuration-table compression levels route through `deflate_slow` in this copy; upstream stored/fast paths are commented out.
- `deflate()` emits the zlib header when called, updates `last_flush`, handles duplicate flush cases, runs the selected compression function, emits empty stored blocks for sync/full flush, clears history on full flush, and writes the Adler trailer at finish.
- `read_buf()` copies input into the sliding window, updates `strm->adler` when wrapping is enabled, and advances stream counters.
- `fill_window()` slides the 32 KiB dictionary, updates head/prev hash tables, reads more input, initializes hash state, and zeroes high-water bytes to avoid longest-match reads from uninitialized memory.
- `longest_match()` walks hash chains up to level-dependent limits, applies good/nice match heuristics, and bounds matches by lookahead.
- `deflate_slow()` performs lazy evaluation: it emits the previous match only if the next position does not produce a better match.
- `deflate_rle()` emits distance-one matches for byte runs and does not maintain hash chains.
- `deflate_huff()` emits only literals and uses Huffman coding without LZ77 matches.

Dependencies:
- Includes `hammer2_zlib_deflate.h`, `../hammer2.h`, and DragonFly malloc definitions.
- Depends on zlib tree helpers `_tr_init`, `_tr_flush_block`, `_tr_flush_bits`, `_tr_align`, `_tr_stored_block`, and tally macros.
- Uses zlib utility macros/functions from `hammer2_zlib_zutil.h`, including `zmemcpy`, `zmemzero`, `ERR_RETURN`, `ERR_MSG`, and constants such as `MAX_WBITS`.

Notable risks:
- Kernel allocation has no application-provided allocator hooks; memory pressure behavior depends on `M_INTWAIT` allocations.
- Level 0 is not true store-only in this copy because stored/fast functions are commented out and mapped to `deflate_slow`.
- Header emission appears unconditional in `deflate()` after reset state setup; any change to status handling must preserve zlib stream correctness.
- Compression state is large and pointer-rich; partial allocation failure must continue to be cleaned by `deflateEnd()`.
- Longest-match code intentionally reads guard bytes beyond valid lookahead, relying on `fill_window()` high-water zeroing for safety.
