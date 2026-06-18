# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/whack.c

`whack.c` implements Venti’s custom LZ77-like compressor. It keeps a rolling hash table of recent 3-byte sequences, searches bounded candidate chains based on compression level, emits optimized literal codes, match lengths, and offset encodings, and abandons compression when output would not fit or progress is poor.

`whackinit()` sizes the search effort and initializes history. `whack()` updates compression statistics, handles match insertion, delay flushing of packed bits, and returns compressed size or `-1`. `whackblock()` is a one-shot helper using level 6.

The format is private to Venti clumps and must match `unwhack.c`. The global `compressblocks` flag can disable compression at runtime.
