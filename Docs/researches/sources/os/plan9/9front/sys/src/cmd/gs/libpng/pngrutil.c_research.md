# File Research: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngrutil.c

This is libpng 1.2.8 internal read-side utility code used by Ghostscript’s bundled libpng copy in the 9front tree. It contains PNG chunk parsing, CRC handling, compressed text/profile decompression, row reconstruction, Adam7 interlace expansion, and row-buffer initialization. It is not filesystem/VFS code; its relevance to subset A is through the complete `sources/os/plan9/9front` source-tree coverage.

Major responsibilities:
- Big-endian scalar readers: `png_get_uint_31`, `png_get_uint_32`, `png_get_int_32`, `png_get_uint_16`.
- CRC path: `png_crc_read`, `png_crc_finish`, and `png_crc_error` read/skip chunk payload bytes and decide whether CRC mismatch is warning or fatal based on critical/ancillary chunk policy flags.
- Compressed ancillary payload handling: `png_decompress_chunk` inflates trailing compressed data for `zTXt`, `iTXt`, and `iCCP`, reallocating output as needed and replacing failed streams with warning/error text behavior.
- Standard chunk handlers: `png_handle_IHDR`, `PLTE`, `IEND`, `gAMA`, `sBIT`, `cHRM`, `sRGB`, `iCCP`, `sPLT`, `tRNS`, `bKGD`, `hIST`, `pHYs`, `oFFs`, `pCAL`, `sCAL`, `tIME`, `tEXt`, `zTXt`, `iTXt`, and unknown chunks.
- Row operations: `png_combine_row`, `png_do_read_interlace`, `png_read_filter_row`, `png_read_finish_row`, and `png_read_start_row`.

Control flow and data flow:
- Chunk handlers enforce PNG ordering rules, validate chunk length and duplicates, read payload through CRC-aware routines, and store validated data through `png_set_*` APIs from `pngset.c`.
- `png_handle_IHDR` initializes `png_struct` image dimensions, bit depth, color type, channel count, rowbytes, and then calls `png_set_IHDR`.
- Metadata handlers generally reject malformed chunks by warning and consuming/skipping remaining bytes with `png_crc_finish`.
- Text/profile handlers allocate a full chunk buffer, locate NUL-separated fields, optionally decompress payload, then pass structured data to `png_set_text_2` or `png_set_iCCP`.
- Unknown chunk handling validates the four-byte chunk name, rejects unknown critical chunks unless configured/user-handled, and optionally saves unknown chunks with location information.
- Row filtering reverses PNG adaptive filters `NONE`, `SUB`, `UP`, `AVG`, and `PAETH`.
- Interlace code expands packed or byte-aligned Adam7 pass rows in place and updates row width/rowbytes.
- `png_read_start_row` computes maximum transformed pixel depth, allocates `big_row_buf`, aligns `row_buf`, allocates `prev_row`, and marks row initialization complete.

Notable implementation details:
- Many handlers are compile-time gated by libpng feature macros.
- `PNG_MAX_MALLOC_64K` paths truncate or reject large ancillary chunks for older memory models.
- Several handlers tolerate technically misplaced chunks with warnings if libpng can still proceed.
- CRC policy distinguishes ancillary and critical chunk behavior using `PNG_FLAG_CRC_*`.
- `png_read_finish_row` drains the zlib stream after the last row and detects extra compressed data.
- Error handling is libpng-style: fatal conditions call `png_error`, warnings call `png_warning` or `png_chunk_warning`.

Important dependencies:
- Public/internal structures and macros from `png.h`.
- zlib `inflate`, `inflateReset`, stream state in `png_ptr->zstream`.
- Storage functions in `pngset.c`.
- Memory and string wrappers such as `png_malloc`, `png_malloc_warn`, `png_free`, `png_memcpy`, `png_strlen`.

Research notes:
- This file is central to PNG read correctness and malformed-input handling.
- It has no direct OS storage, block, filesystem, or VFS behavior.
- Potential audit points are memory allocation size calculations, older 64K compatibility paths, compressed text/profile decompression limits, and unknown critical chunk policy.
