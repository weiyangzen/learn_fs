# File Research: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngwutil.c

This is the libpng 1.2.8 write-side utility implementation vendored under the 9front Ghostscript tree. It is compiled only when `PNG_WRITE_SUPPORTED` is enabled and provides the low-level chunk writers, ancillary chunk encoders, row filtering, interlace compaction, and zlib output pipeline for PNG generation.

Key responsibilities:
- Writes PNG integers in network byte order with `png_save_uint_32`, `png_save_int_32`, and `png_save_uint_16`.
- Implements generic chunk emission through `png_write_chunk`, `png_write_chunk_start`, `png_write_chunk_data`, and `png_write_chunk_end`, including CRC handling.
- Writes PNG signature, core chunks, and end chunks: `png_write_sig`, `png_write_IHDR`, `png_write_PLTE`, `png_write_IDAT`, and `png_write_IEND`.
- Emits many optional ancillary chunks under feature macros: `gAMA`, `sRGB`, `iCCP`, `sPLT`, `sBIT`, `cHRM`, `tRNS`, `bKGD`, `hIST`, `tEXt`, `zTXt`, `iTXt`, `oFFs`, `pCAL`, `sCAL`, `pHYs`, and `tIME`.
- Handles compressed text and ICC payload buffering through a local `compression_state` structure plus `png_text_compress` and `png_write_compressed_data_out`.
- Initializes row-writing state with `png_write_start_row`, advances/interlace-flushes with `png_write_finish_row`, compacts Adam7 pass pixels in `png_do_write_interlace`, chooses filters in `png_write_find_filter`, and sends filtered rows to zlib in `png_write_filtered_row`.

Important control flow:
- `png_write_IHDR` validates color type, bit depth, compression, filter, and interlace mode, then stores derived row metadata on `png_ptr` and initializes zlib with configured compression strategy, level, memory level, window bits, and method.
- `png_write_IDAT` contains a small zlib CMF optimization before the first IDAT, reducing the advertised compression window for small images when safe.
- Text writing is length-first: zTXt, iTXt, and iCCP compress into saved buffers so the chunk length can be known before output.
- Row filtering computes the PNG filter byte plus filtered row bytes, using minimum sum of absolute differences and optional weighted filter heuristics.

Notable implementation details and risks:
- This is old vendored libpng code, not 9front-native filesystem code. Its relevance to the subset is as part of the `sources/os/plan9/9front` source tree, specifically Ghostscript PNG output support.
- The code has many compile-time feature gates, so actual behavior depends heavily on libpng configuration macros.
- Memory allocation is through libpng hooks such as `png_malloc`, `png_malloc_warn`, and `png_free`.
- Error handling uses libpng `png_error` and `png_warning`, which can longjmp depending on caller setup.
- There is a suspicious legacy line in `png_check_keyword`: `new_key[79] = '\0';` appears to index the pointer-to-pointer rather than `(*new_key)[79]`. This should be treated as vendored historical behavior unless auditing libpng correctness.
- The `PNG_NO_POINTER_INDEXING` branch in `png_write_sPLT` uses `for (i=0; i>spalette->nentries; i++)`, which would not iterate for positive counts. Again, this is vendored historical code.
- No direct filesystem, VFS, block, or storage abstractions are present. I/O is delegated to `png_write_data` callbacks.

Research classification: vendored third-party image encoding utility inside Ghostscript, operationally unrelated to kernel filesystem logic but part of the 9front source inventory.
