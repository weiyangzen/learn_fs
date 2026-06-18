# File Research: sources/os/plan9/9front/sys/src/cmd/disk/sacfs/sac.c

## Purpose
Implements the SAC block compressor used by `mksacfs`.

## Key Behavior
- Compresses one block with a Burrows-Wheeler transform driven by `ssortbyte()`, move-to-front encoding, zero-run encoding, and custom length-limited Huffman coding.
- Emits the BWT primary index, a compact character-presence map, Huffman table descriptions, and encoded symbol stream into a caller-supplied destination buffer.
- Tracks output bounds with `bitput()` and returns `-1` through `longjmp` when compressed data would exceed the source block size.
- Encodes runs of zero MTF symbols with a binary run-length representation using `ZBase`/`LitBase`.
- Builds Huffman code lengths with a fast in-place minimum-redundancy path when possible, falling back to a package-merge style length-limited algorithm for `MaxHuffBits`.
- Serializes Huffman tables with nested Huffman coding over move-to-front code lengths.
- Includes local sorting for leaf frequency maps and canonical Huffman code assignment.

## Interfaces And Dependencies
- Public entry point is `int sac(uchar *dst, uchar *src, int n)`.
- Uses `ssortbyte()` from `ssort6.c` declared in `ssort.h`.
- Shares constants and the corresponding decompressor format with `unsac.c`.

## Notes
The compressor mutates global static encoder state for one block at a time and is not reentrant. Compression failure is expected and simply causes the image builder to store the original block.
