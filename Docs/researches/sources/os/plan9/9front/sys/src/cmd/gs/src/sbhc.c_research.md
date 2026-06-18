# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sbhc.c

Implements BoundedHuffman encode and decode filters. These extend the common Huffman stream machinery with zero-run encoding and optional end-of-data markers.

The encoder allocates an encoding table from the supplied Huffman definition, accumulates runs of zero values, emits zero-run codes where possible, writes optional EOD, and flushes pending bits. The decoder allocates a decoding table, decodes variable-length codes, expands zero runs, and recognizes EOD.

Dependencies include `sbhc.h`, `shcgen.h`, Ghostscript memory allocation, and the Huffman encoder/decoder state macros from `shc.h`.

Risk notes: the file contains historical `WRONG` and `NOT IMPLEMENTED YET` comments around table generation assumptions and incomplete partial-code handling. This is compression stream code, not filesystem code.
