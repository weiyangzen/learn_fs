# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/shc.c

Support routines for Huffman-coded stream helpers declared in `shc.h`.

Key behavior:
- `hc_put_code_proc` writes a full buffered Huffman code word to output, optionally reversing bits per byte for low-order-first encodings.
- `hc_put_last_bits_proc` flushes final partial bits one byte at a time, applying bit reversal when needed, and stores updated bit-buffer state back into the stream state.

Notable dependencies:
- `shc.h` for state and bit-size definitions.
- `gsbittab.h` through `shc.h` for `byte_reverse_bits`.

Research notes:
- Most Huffman work is macro-based in `shc.h`; this file contains the out-of-line routines used when buffered output crosses word boundaries or needs final flushing.
