# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jcinit.c

Full-compressor module selection and initialization.

Key points:
- `jinit_compress_master` initializes master control for full compression.
- If not using raw data input, initializes color conversion, downsampling, and preprocessing controllers.
- Always initializes forward DCT.
- Selects entropy encoder: arithmetic coding is unimplemented; progressive mode uses progressive Huffman when compiled; otherwise sequential Huffman.
- Initializes coefficient controller with full buffering when multiscans or optimized Huffman coding require it.
- Initializes main controller, marker writer, realizes virtual arrays, and writes SOI immediately while delaying frame/scan headers.

Dependencies and interactions:
- Split from `jcmaster.c` so transcoders can use master logic without linking the full pixel pipeline.
- Calls almost every compressor module initializer in the normal path.

Risk notes:
- Arithmetic coding is a hard error.
- Progressive compression requires `C_PROGRESSIVE_SUPPORTED`.
- Marker header design intentionally permits application APP/COM marker insertion after SOI and before first scan data.
