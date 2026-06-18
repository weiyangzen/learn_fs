# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sdcparam.h

Internal header for DCT filter parameter helpers implemented in `sdcparam.c`.

It declares routines for:

- Common DCT parameter get/put.
- Quantization table get/put.
- Huffman table get/put.
- Byte-sized parameter extraction from strings or arrays.

The comments state these are internal helpers used by `sddparam.c` and `sdeparam.c`, not public API.

This is DCT/JPEG stream parameter interface code, not filesystem logic.
