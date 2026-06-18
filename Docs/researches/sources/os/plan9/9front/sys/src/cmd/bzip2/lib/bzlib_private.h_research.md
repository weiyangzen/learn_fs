# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzlib_private.h

Purpose: Private libbzip2 header for the 9front bzip2 copy, marked as modified from the upstream bzip2 distribution mainly to split the library into smaller pieces.

Key points:
- Defines `BZ_VERSION` as `1.0.1, 23-June-2000`.
- Provides internal assertion, verbose logging, allocation, CRC, randomization, compression-state, and decompression-state macros.
- Defines compression-side `EState`, including block sort arrays, bitstream output fields, CRCs, MTF/Huffman coding tables, selector arrays, and block metadata.
- Defines decompression-side `DState`, including resumable parser state, bitstream input buffer, BWT inverse structures for fast and small modes, CRC state, MTF tables, Huffman decode tables, and saved local variables for coroutine-style decompression.
- Declares internal compression, decompression, Huffman, CRC, allocation, and configuration functions.

Dependencies and interactions:
- Depends on public `bz_stream` and bzip2 typedefs from `bzlib.h`, plus platform typedefs from `os.h`.
- `compress.c`, `decompress.c`, `huffman.c`, `bzread.c`, `bzwrite.c`, and table files rely on these structs and macros.
- CRC macros use `BZ2_crc32Table` from `crctable.c`.
- Randomized block compatibility uses `BZ2_rNums` from `randtable.c`.

Research notes:
- This is the central internal ABI for the split bzip2 library. Changes here affect nearly every bzip2 translation unit.
- The decompressor keeps extensive save fields, which explains the macro-heavy parser in `decompress.c`.
