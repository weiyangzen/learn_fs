# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzdecompress.c

Core streaming decompression state machine for libbzip2.

Provides:

- `BZ2_bzDecompressInit()`: validates config, installs allocators, initializes `DState`.
- `unRLE_obuf_to_output_FAST()`: inverse BWT/output run decoder using `tt`.
- `unRLE_obuf_to_output_SMALL()`: memory-saving inverse path using `ll16`/`ll4`.
- `BZ2_indexIntoF()`: helper for small-mode inverse mapping.
- `BZ2_bzDecompress()`: drives parser state through `BZ2_decompress()`, emits output, validates per-block and combined CRCs, and returns `BZ_OK`, `BZ_STREAM_END`, or data errors.
- `BZ2_bzDecompressEnd()`: frees decompression state arrays.

It handles both randomized and non-randomized historical bzip2 blocks and preserves partial output state when caller output buffers fill.
