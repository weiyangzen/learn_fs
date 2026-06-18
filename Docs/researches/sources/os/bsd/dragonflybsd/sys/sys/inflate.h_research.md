# File Research: sources/os/bsd/dragonflybsd/sys/sys/inflate.h

`inflate.h` declares a small reentrant gzip/deflate inflate interface for kernel or `KZIP` builds. It defines `GZ_EOF` and `GZ_WSIZE`.

`struct inflate` carries caller-private data, input and output callbacks, and private inflate state such as bit buffer, bit count, memory-use tracking, fixed Huffman table pointers, fixed table bit widths, sliding window, and write pointer.

It declares `inflate(struct inflate *)`. The callback-based state object makes the decompressor reusable without global mutable state.
