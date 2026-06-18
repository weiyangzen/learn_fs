# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sdcparam.c

Implements common DCT/JPEG filter parameter get/put logic. It handles scalar DCT parameters (`ColorTransform`, `QFactor`) and JPEG stream data flags (`Picky`, `Relax`), plus quantization and Huffman table serialization/deserialization.

Quantization handling converts between Adobe zigzag order and IJG natural order for newer JPEG versions, supports byte strings and float arrays, applies `QFactor`, detects duplicate tables, assigns component table numbers, and allocates missing IJG quant tables through Ghostscript JPEG allocation helpers.

Huffman handling packs/unpacks the 16 count bytes plus values, supports byte string or float-array input via `s_DCT_byte_params`, detects duplicate DC/AC tables, assigns component table numbers, and enforces baseline or relaxed table-count limits.

Dependencies include `jpeglib_.h`, `sdct.h`, `sdcparam.h`, `sjpeg.h`, Ghostscript parameter APIs, and memory/error utilities.

Risk notes: comments mark some deallocation paths and byte-array handling as historically imperfect. This is JPEG stream parameter plumbing.
