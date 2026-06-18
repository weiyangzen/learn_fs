# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sddparam.c

Implements `DCTDecode` parameter get/put wrappers. `s_DCTD_get_params` creates default DCT state and delegates common scalar parameter writing to `s_DCT_get_params`; a comment marks fuller decode parameter reporting as not yet implemented.

`s_DCTD_put_params` applies common DCT scalar parameters, then accepts Huffman and quantization tables for decode streams so missing tables can be supplied externally.

Dependencies include `jpeglib_.h`, `sdct.h`, `sdcparam.h`, `sjpeg.h`, and Ghostscript parameter/error APIs.

This is JPEG decode parameter handling.
