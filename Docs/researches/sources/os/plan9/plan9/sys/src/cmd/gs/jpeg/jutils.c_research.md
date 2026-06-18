# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jutils.c

This file provides shared IJG utility data and routines used by compression and decompression code.

Its main exported table is `jpeg_natural_order[DCTSIZE2+16]`, mapping zigzag coefficient order back to natural 8x8 block order. The trailing sixteen entries are all `63`, intentionally preventing wild stores if corrupted Huffman data produces a run past the end of a block.

The arithmetic helpers `jdiv_round_up()` and `jround_up()` implement ceiling division and rounding to a multiple, assuming nonnegative input and positive divisor.

The memory helpers are `jcopy_sample_rows()`, `jcopy_block_row()`, and `jzero_far()`. They abstract ordinary memory copying/zeroing versus FAR-pointer memory models, using `FMEMCOPY`/`FMEMZERO` when available and byte/element loops otherwise.

Dependencies are `jinclude.h`, `jpeglib.h`, compile-time memory model macros, and core libjpeg typedefs such as `JSAMPARRAY`, `JBLOCKROW`, `JCOEF`, and `JDIMENSION`. This is low-level portability support, not Plan 9 filesystem code.
