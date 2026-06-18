# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sdcparam.c

Shared DCT/JPEG filter parameter handling for Ghostscript’s `DCTEncode` and `DCTDecode`.

Major responsibilities:

- Defines common DCT scalar parameters `ColorTransform` and `QFactor`, plus IJG wrapper flags `Picky` and `Relax`.
- Converts Adobe zigzag-order quantization parameters to IJG natural order for newer JPEG library versions, and back when reporting parameters.
- Reads/writes quantization tables as strings or float arrays under `QuantTables`.
- Packs and writes Huffman tables under `HuffTables`.
- Reads byte-sized parameters from strings or float arrays through `s_DCT_byte_params`.
- Validates common scalar ranges, including `Picky`, `Relax`, `ColorTransform`, and `QFactor`.
- Deduplicates identical quantization and Huffman tables and assigns component table indexes.
- Allocates IJG quantization/Huffman tables through Ghostscript JPEG allocation helpers.

Risk notes: several comments note incomplete deallocation on intermediate errors and a “byte_array IS WRONG” legacy concern. The code assumes valid IJG table pointers in some get paths.

This is JPEG/DCT stream parameter plumbing, not filesystem code.
