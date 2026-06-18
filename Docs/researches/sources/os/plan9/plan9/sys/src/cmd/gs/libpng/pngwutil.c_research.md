# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngwutil.c

This is libpng 1.2.8 write-side utility code embedded in the Plan 9 Ghostscript source tree. It is not filesystem code; it supports Ghostscript PNG output by serializing PNG chunks, compressing image/text data, selecting scanline filters, and writing IDAT streams.

Core responsibilities:
- Provides endian-safe helpers for PNG integer encoding: `png_save_uint_32`, `png_save_int_32`, and `png_save_uint_16`.
- Implements generic chunk emission through `png_write_chunk_start`, `png_write_chunk_data`, and `png_write_chunk_end`, including CRC calculation over chunk type and payload.
- Writes the PNG signature and critical chunks: `IHDR`, `PLTE`, `IDAT`, and `IEND`.
- Writes optional ancillary chunks under feature macros: `gAMA`, `sRGB`, `iCCP`, `sPLT`, `sBIT`, `cHRM`, `tRNS`, `bKGD`, `hIST`, text chunks, `oFFs`, `pCAL`, `sCAL`, `pHYs`, and `tIME`.
- Drives zlib initialization and buffering for image rows and compressed text/profile chunks.
- Handles Adam7 interlace row compaction and PNG filter selection/writing.

Important implementation details:
- `png_write_IHDR` validates bit depth/color type combinations, normalizes invalid compression/filter/interlace settings with warnings where possible, initializes row metadata, configures zlib defaults, and starts the write-mode state machine with `PNG_HAVE_IHDR`.
- Text and profile compression is staged through a local `compression_state`, allowing compressed output length to be known before starting the containing chunk.
- `png_check_keyword` sanitizes PNG text keywords by replacing invalid characters, trimming leading/trailing spaces, collapsing repeated internal spaces, and enforcing the 79-byte keyword maximum.
- `png_write_IDAT` adjusts the first zlib CMF/FLG bytes for small images to reduce advertised window size, then writes the IDAT chunk.
- `png_write_start_row`, `png_write_finish_row`, `png_write_find_filter`, and `png_write_filtered_row` together allocate filter buffers, compute filter heuristics, stream rows through deflate, and flush final IDAT bytes.
- Optional weighted filter heuristics are guarded by `PNG_WRITE_WEIGHTED_FILTER_SUPPORTED`.

Notable risks/quirks:
- This is old libpng code, so modern security expectations should not be inferred from it.
- In `png_check_keyword`, the truncation branch assigns `new_key[79] = '\0'`, which appears suspicious because `new_key` is a `png_charpp`; the intended write is likely through `*new_key`.
- In the `PNG_NO_POINTER_INDEXING` branch of `png_write_sPLT`, the loop condition reads `i>spalette->nentries`, which means that fallback branch would not iterate from zero as expected.
- Many functions are conditionally compiled, so actual behavior depends heavily on `PNG_WRITE_*` macros from the surrounding Ghostscript/libpng build.
- Filesystem relevance is indirect only: PNG output may write through Ghostscript output streams, but this file does not implement OS file I/O or VFS behavior.
