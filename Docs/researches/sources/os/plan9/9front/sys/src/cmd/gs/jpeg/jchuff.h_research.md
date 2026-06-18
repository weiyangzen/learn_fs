# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jchuff.h

Private shared declarations for sequential and progressive Huffman compression.

Key points:
- Defines `MAX_COEF_BITS` as 10 for 8-bit samples and 14 otherwise, matching expected DCT coefficient magnitude ranges.
- Defines `c_derived_tbl`, holding encoder-side Huffman code and code-length lookup arrays for all possible byte-sized symbols.
- Declares `jpeg_make_c_derived_tbl` for expanding a public `JHUFF_TBL` into encoder lookup form.
- Declares `jpeg_gen_optimal_table` for building an optimal/length-limited public Huffman table from symbol frequencies.
- Provides short external-name aliases for constrained linkers.

Dependencies and interactions:
- Included by `jchuff.c` and `jcphuff.c` only.
- Depends on public compressor types from `jpeglib.h`.

Risk notes:
- This is private compressor infrastructure; other modules should not depend on it.
- Coefficient magnitude assumptions are tied to IJG’s supported 8-bit/12-bit sample modes.
