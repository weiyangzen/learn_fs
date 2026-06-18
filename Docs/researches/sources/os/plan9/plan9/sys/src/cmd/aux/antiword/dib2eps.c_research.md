# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/dib2eps.c

This file translates embedded DIB bitmap images into EPS-compatible encoded image data.

Key behavior:
- Decodes uncompressed 1, 4, 8, and 24 bits-per-pixel DIB pixel data.
- Decodes RLE4 and RLE8 compressed bitmap data, handling end-of-line, end-of-file, literal packets, and basic escape handling.
- Skips bitmap info headers, color tables, and row padding.
- Converts 24-bit BGR input into RGB output.
- Emits decoded pixels via the ASCII85 encoder between image prologue and epilogue hooks.
- In debug builds, can dump DIB data as BMP-like files under `/tmp/pic`.

Important details:
- Input bytes come from `datalist.c` through `iNextByte()` and `tSkipBytes()`.
- Delta escapes in RLE streams terminate decoding rather than applying offsets.
- `bTranslateDIB()` first positions the data cursor with `bSetDataOffset()`.

Filesystem relevance:
- Indirect but storage-aware: reads embedded image streams from Word file data blocks and emits converted output.
