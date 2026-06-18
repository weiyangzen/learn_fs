# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzlib_private.h

Private libbzip2 header for the Plan 9 split of bzip2 1.0.1. It defines shared constants, assertion/verbosity macros, allocator macros, CRC/randomisation helpers, compression/decompression states, and the internal `EState` and `DState` structs.

`EState` holds compression-side block buffers, block sorting aliases, run-length state, CRCs, bitstream writer state, selectors, Huffman lengths/codes, and MTF frequencies. `DState` holds decompression state-machine state, bitstream reader state, fast/small inverse BWT buffers, CRCs, selector/Huffman decode tables, MTF decode arrays, and saved locals for resumable decompression.

This file is central glue for all bzip2 library modules in this directory. It declares internal entry points such as `BZ2_blockSort`, `BZ2_compressBlock`, `BZ2_decompress`, Huffman helpers, default allocation, and config checks. The Plan 9 modification note says the original library was split into smaller pieces by Russ Cox.
