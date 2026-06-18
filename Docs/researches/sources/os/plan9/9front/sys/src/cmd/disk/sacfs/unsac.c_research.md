# File Research: sources/os/plan9/9front/sys/src/cmd/disk/sacfs/unsac.c

## Purpose
Implements SAC block decompression, the inverse of `sac.c`.

## Key Behavior
- `unsac()` decodes one compressed block from a source buffer into a fixed-size destination block.
- Reads the BWT primary index and character-presence map, reconstructs the initial move-to-front alphabet, decodes Huffman tables, and then decodes the symbol stream.
- Uses an optimized MTF list with comb indices for faster indexed removal/move-to-front operations.
- Reverses the custom zero-run encoding used by the compressor.
- `hdecblock()` combines Huffman decode, move-to-front decode, character counting, and LF-mapping predecessor construction.
- Reconstructs the original byte order by walking predecessor links backward from the BWT primary index.
- Builds canonical Huffman decoding tables including flat prefix tables for fast short-code decoding.
- Uses `setjmp`/`longjmp` for corruption/allocation/EOF failures and returns `-1` to the caller.

## Interfaces And Dependencies
- Public entry point is `int unsac(uchar *dst, uchar *src, int n, int nsrc)`.
- Shares format constants with `sac.c` through duplicated local enums and `sac.h`.
- Called by `sacfs.c` when a block-table offset is negative.

## Notes
The decompressor prints some corruption messages via `fatal()` before jumping back. It assumes the caller knows the uncompressed block size and compressed byte length from the SAC block offset table.
