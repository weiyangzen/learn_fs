# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/huffman.c

Purpose: Provides low-level Huffman code generation and decode table construction for bzip2.

Key points:
- `BZ2_hbMakeCodeLengths` builds Huffman code lengths from symbol frequencies using heap operations and retries with adjusted weights if lengths exceed `maxLen`.
- `BZ2_hbAssignCodes` assigns canonical Huffman codes by code length.
- `BZ2_hbCreateDecodeTables` builds `limit`, `base`, and `perm` decode tables from code lengths.

Dependencies and interactions:
- Used by `compress.c` to generate code lengths and assign canonical codes.
- Used by `decompress.c` to build decode tables.
- Uses constants and assertions from `bzlib_private.h`.

Research notes:
- Heap and weight macros pack frequency and depth into integer weights.
- The implementation assumes bzip2’s maximum alphabet and code length constraints.
