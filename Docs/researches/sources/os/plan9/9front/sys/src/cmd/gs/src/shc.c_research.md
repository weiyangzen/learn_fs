# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/shc.c

Provides support routines for Huffman-coded stream macros.

Key points:
- `hc_put_code_proc` writes the accumulated word-sized bit buffer to output, optionally reversing bits in each byte for low-order-first encodings.
- Handles both 16-bit and wider `uint` buffer sizes via `hc_bits_size`.
- `hc_put_last_bits_proc` flushes remaining partial bytes at stream end, applying bit reversal when `FirstBitLowOrder` is set.
- Updates `stream_hc_state.bits` and `bits_left` after final flushing.

Dependencies and interactions:
- Implements helper calls used by `shc.h` macros rather than standalone filters.
- Relies on `byte_reverse_bits` from bit-table support.

Research relevance:
- Small but central bit-emission support for Huffman encoders such as fax filters.
