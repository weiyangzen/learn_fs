# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jctrans.c

Compression-side support for coefficient transcoding.

Key points:
- `jpeg_write_coefficients` starts a compression object for writing preexisting virtual DCT coefficient arrays, unsuppresses tables, initializes destination/error managers, selects transcoding modules, and enters `CSTATE_WRCOEFS`.
- `jpeg_copy_critical_parameters` copies image dimensions, color space, precision, CCIR601 flag, quantization tables, component IDs/sampling/quant table assignments, and JFIF density/version data from a decompressor to a compressor for lossless transcoding.
- It verifies that component-private quantization tables match their referenced quant table slots, rejecting files that reuse a slot incompatibly.
- `transencode_master_selection` initializes master control in transcode-only mode, selects Huffman/progressive Huffman entropy encoder, installs a special coefficient controller, initializes marker writer, realizes arrays, and writes SOI/APP markers.
- Special coefficient controller reads caller-supplied virtual block arrays and creates dummy padding blocks on the fly for right/bottom edges.
- `compress_output` walks active scan MCUs from virtual arrays and feeds entropy encoding.

Dependencies and interactions:
- Paired with decompression-side coefficient readers in `jdtrans.c` outside this group.
- Uses `jcmaster.c`, entropy encoders, marker writer, and memory manager virtual block arrays.

Risk notes:
- Arithmetic transcoding is unimplemented.
- Cannot represent source JPEGs whose components have saved quant tables that differ from their referenced quant table slots.
- Caller must supply coefficient arrays matching component block dimensions and virtual-array unit-height requirements.
