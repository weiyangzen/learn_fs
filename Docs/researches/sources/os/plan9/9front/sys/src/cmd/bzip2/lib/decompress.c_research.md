# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/decompress.c

Purpose: Implements bzip2 stream decompression parsing and block setup.

Key points:
- Uses macros `GET_BITS`, `GET_UCHAR`, `GET_BIT`, and `GET_MTF_VAL` to implement a resumable state machine over `DState.state`.
- Validates stream magic `BZh1` through `BZh9`, allocates either fast `tt` storage or small `ll16/ll4` storage.
- Parses block headers, block CRC, randomization flag, original pointer, mapping table, selector list, Huffman code lengths, and MTF/RLE data.
- Builds Huffman decode tables with `BZ2_hbCreateDecodeTables`.
- Reconstructs byte frequency tables and inverse BWT traversal structures.
- Handles both old randomized blocks and normal non-randomized blocks.
- Parses stream trailer and stored combined CRC, returning `BZ_STREAM_END`.

Dependencies and interactions:
- Uses `DState` and decompression macros from `bzlib_private.h`.
- Calls `BZ2_hbCreateDecodeTables` from `huffman.c`.
- Uses allocation callbacks via `BZALLOC`.
- The output phase itself is coordinated with other decompression routines using `DState.state_out_*`, `tPos`, `k0`, and `nblock_used`.

Research notes:
- This file is designed for incremental input: when input is exhausted, it saves local parser state into `DState` and returns `BZ_OK`.
- It performs strong structural validation, returning data errors for impossible selectors, code lengths, MTF values, out-of-range original pointers, and block overflow.
