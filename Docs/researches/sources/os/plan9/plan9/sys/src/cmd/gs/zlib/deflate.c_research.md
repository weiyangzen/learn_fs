# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/deflate.c

## Purpose
Implements zlib 1.2.2 deflate compression: stream initialization, parameter changes, dictionary setup, block generation, sliding-window matching, flushing, trailers, copying, and teardown.

## Public Surface
- `deflateInit_`, `deflateInit2_`.
- `deflateSetDictionary`.
- `deflateReset`.
- `deflatePrime`.
- `deflateParams`.
- `deflateBound`.
- `deflate`.
- `deflateEnd`.
- `deflateCopy`.

## Implementation Notes
- Configuration table maps compression levels to match parameters and compressor functions: stored, fast, or slow.
- `deflateInit2_` validates zlib version/stream size, selects zlib/raw/gzip wrapper from `windowBits`, allocates window, hash chains, hash heads, and pending/literal/distance buffers.
- `deflateSetDictionary` seeds the window and hash chains and updates Adler state unless raw/gzip rules reject it.
- `deflateReset` resets counters, wrapper state, checksum, Huffman tree state, and LZ77 match state.
- `deflateParams` can switch compression level/strategy midstream and flushes if compressor function changes.
- `deflate` writes zlib or gzip headers, drains pending bytes, handles duplicate flush semantics, invokes the selected block compressor, writes empty flush blocks, handles `Z_FULL_FLUSH` history clearing, and emits zlib/gzip trailers on finish.
- `deflateEnd` frees pending buffer, hash heads, previous links, window, and state.
- `deflateCopy` deep-copies a stream state except on 16-bit `MAXSEG_64K`.
- `fill_window` maintains the 2x window, slides the upper half down, adjusts hash chains, reads input, and initializes rolling hash.
- `deflate_stored` emits uncompressed stored blocks for level 0.
- `deflate_fast` performs greedy matching without lazy evaluation.
- `deflate_slow` performs lazy match evaluation for better compression.
- `longest_match` and `longest_match_fast` implement hash-chain match searches with careful lookahead and optimization assumptions.

## Dependencies
Depends on `deflate.h`, zlib utility allocators/memory helpers/checksums, Huffman tree functions from `trees.c`, and optional asm match support.

## Risks and Notes
- Window sliding and hash-chain updates are correctness-critical.
- Wrapper state uses sign changes to prevent duplicate trailers.
- Strategy-specific match suppression affects compression ratio and deterministic output.
- `deflateEnd` returns `Z_DATA_ERROR` if ending while busy.
- Filesystem relevance: none directly; compression library used by Ghostscript streams/builds.
