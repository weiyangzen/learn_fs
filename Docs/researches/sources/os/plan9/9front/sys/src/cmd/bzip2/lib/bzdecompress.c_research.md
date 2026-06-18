# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzdecompress.c

This is the low-level streaming decompression state machine for libbzip2.

Major responsibilities:
- `BZ2_bzDecompressInit`: validates options, allocates `DState`, initializes bitstream and output state.
- Converts inverse-BWT output into un-RLE’d bytes for both fast and small modes.
- `BZ2_bzDecompress`: alternates between block decoding and output draining.
- Validates per-block CRC and combined CRC.
- `BZ2_bzDecompressEnd`: frees `tt`, `ll16`, `ll4`, and state.

Notable implementation details:
- Fast path uses cached local variables in `unRLE_obuf_to_output_FAST` for speed.
- Supports randomized and non-randomized legacy bzip2 blocks.
- `BZ2_indexIntoF` supports small decompression table walking.
- Returns `BZ_OK` when more output/input progress is needed and `BZ_STREAM_END` after final CRC validation.

Risks and caveats:
- Depends on `BZ2_decompress` from the decompression parser file.
- CRC mismatch returns `BZ_DATA_ERROR`.
