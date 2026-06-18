# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jchuff.h

Private Huffman encoder declarations shared by sequential and progressive compressor modules.

Key contents:
- Defines `MAX_COEF_BITS` as 10 for 8-bit samples and 14 otherwise.
- Defines `c_derived_tbl`, the encoder-side expanded Huffman table containing code and code-length entries for every possible symbol.
- Provides short external-name aliases when `NEED_SHORT_EXTERNAL_NAMES` is enabled.
- Declares `jpeg_make_c_derived_tbl` and `jpeg_gen_optimal_table`.

Dependencies:
- Requires IJG compressor types, Boolean type, and Huffman table definitions from the surrounding JPEG headers.

Notable risks:
- This is not a public application header; comments explicitly limit it to `jchuff.c` and `jcphuff.c`.
