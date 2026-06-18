# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/huffman.c

Low-level Huffman support for bzip2. `BZ2_hbMakeCodeLengths` builds bounded-length code lengths from symbol frequencies using heap-based tree construction and frequency rescaling if any code exceeds `maxLen`.

`BZ2_hbAssignCodes` assigns canonical Huffman codes from lengths. `BZ2_hbCreateDecodeTables` builds decoder `limit`, `base`, and `perm` tables from lengths for min/max code lengths.

The implementation uses local fixed arrays sized from `BZ_MAX_ALPHA_SIZE` and assertion checks for heap/node bounds.
