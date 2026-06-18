# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdhuff.h

Private shared declarations for sequential and progressive Huffman decompression.

Key points:
- Defines `d_derived_tbl`, containing max-code, value-offset, public table backlink, and 8-bit lookahead decode tables.
- Declares `jpeg_make_d_derived_tbl`, `jpeg_fill_bit_buffer`, and `jpeg_huff_decode`.
- Defines permanent and working bit-buffer state structures; working state copies source pointers to support suspension rollback.
- Provides `CHECK_BIT_BUFFER`, `GET_BITS`, `PEEK_BITS`, and `DROP_BITS` macros for hot entropy loops.
- Provides `HUFF_DECODE`, a fast lookahead-first symbol decoder with slow-path fallback for longer codes.
- Includes short external-name aliases for constrained linkers.

Dependencies and interactions:
- Included only by `jdhuff.c` and `jdphuff.c`.
- Assumes JPEG Huffman code requests never exceed 15 bits at once.

Risk notes:
- Macro arguments are evaluated in tightly constrained ways; callers must pass simple variables for bit counts.
- Bit-buffer type/size choices are fixed at 32-bit `INT32` here unless ported deliberately.
- This header exposes private entropy internals and should not become a general module dependency.
