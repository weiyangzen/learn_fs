# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/rdppm.c

IJG `cjpeg` input module for PPM/PGM images, compiled when `PPM_SUPPORTED` is enabled. It supports text PGM/PPM (`P2`, `P3`), raw byte PGM/PPM (`P5`, `P6`), and extended raw word-per-sample variants.

Main data structures and entry points:
- `ppm_source_struct` extends `cjpeg_source_struct` with an IO row buffer, sample row pointer, buffer width, and optional maxval rescale table.
- `jinit_read_ppm` allocates the source object and installs `start_input_ppm`/`finish_input_ppm`.
- `start_input_ppm` validates the magic, reads width/height/maxval, sets compressor image metadata, selects a row reader, and allocates IO/sample buffers.
- `pbm_getc` and `read_pbm_integer` parse PBMPLUS-style headers and text sample data while skipping `#` comments.

Row readers:
- `get_text_gray_row` and `get_text_rgb_row` parse ASCII samples and rescale through `source->rescale`.
- `get_scaled_gray_row` and `get_scaled_rgb_row` read 8-bit raw samples and rescale when maxval differs from `MAXJSAMPLE`.
- `get_raw_row` reads directly into the JSAMPLE buffer for the common 8-bit/maxval case.
- `get_word_gray_row` and `get_word_rgb_row` read two-byte samples and rescale them to `BITS_IN_JSAMPLE`.

Important behavior:
- The rescale table maps arbitrary positive maxval values to JPEG sample range using 32-bit arithmetic to avoid overflow.
- For direct raw reads, `source->pub.buffer` points at the IO buffer through a synthesized `JSAMPARRAY`.
- The code assumes the caller starts reading at the beginning of the file.

Filesystem relevance:
- Sequential image-file reader only. It contributes format parsing and buffering patterns, not filesystem semantics.
