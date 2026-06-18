# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jctrans.c

Compression support for coefficient-level JPEG transcoding.

Key behavior:
- `jpeg_write_coefficients` starts a compression object that writes preexisting virtual DCT coefficient arrays instead of accepting sample rows.
- Marks all tables for output, initializes the destination, selects transcoding modules, writes SOI, and enters `CSTATE_WRCOEFS` pending `jpeg_finish_compress`.
- `jpeg_copy_critical_parameters` copies dimensions, colorspace, precision, sampling, quantization tables, component IDs/factors/table selectors, and JFIF density/version from a decompressor to a compressor.
- Verifies saved per-component quantization tables match the source table slots, rejecting cases this encoder cannot duplicate.
- Provides a special coefficient controller that reads supplied coefficient virtual arrays and generates dummy padding blocks at image edges on the fly.

Dependencies:
- Uses decompressor-side parsed metadata, compressor parameter defaults, marker writer, Huffman/progressive entropy encoders, and virtual block arrays.

Notable risks:
- Arithmetic transcoding output is rejected as not implemented.
- Huffman table assignments are not copied from the source; defaults or later caller changes are used.
- Dummy block generation assumes prior block DC values are available when padding at right/bottom edges.
