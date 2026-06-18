# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/rdbmp.c

Purpose: `cjpeg` input module for reading Microsoft/OS/2 BMP files and presenting them as RGB sample rows to the JPEG compressor.

Key contents:
- Compiled only when `BMP_SUPPORTED` is enabled.
- Defines unsigned-byte helper type/macros and `ReadOK`.
- `bmp_source_struct` extends `cjpeg_source_struct` with compressor back link, BMP colormap, virtual image array, row counters, physical row width, and bit depth.
- `read_byte()` reads one byte or raises `JERR_INPUT_EOF`.
- `read_colormap()` reads OS/2 BGR or Windows BGR0 palette entries into RGB colormap arrays.
- Row readers: `get_8bit_row()` expands palette indexes to RGB; `get_24bit_row()` converts file BGR bytes to RGB.
- `preload_image()` reads the BMP pixel data into a virtual array before row output.
- `start_input_bmp()` parses BMP headers, validates format, reads colormap, skips padding, configures virtual storage and compressor image parameters.
- Public init entry: `jinit_read_bmp()`.

Important behavior:
- Supports 8-bit colormapped and 24-bit BMP only.
- Supports OS/2 1.x 12-byte headers, Windows 40-byte headers, and OS/2 2.x 64-byte headers.
- Rejects 1-bit, 4-bit, unsupported depths, multiple planes, compressed BMPs, invalid headers, and bad colormaps.
- BMP rows are stored bottom-up in files; this module preloads the entire image into a virtual array and emits rows top-down.
- Computes physical row width including 4-byte BMP scanline padding.
- For Windows/OS2 headers with positive pels-per-meter values, sets JFIF density as dots/cm.
- Sets compressor input as 8-bit `JCS_RGB` with three components.

Dependencies:
- `cdjpeg.h`, IJG memory manager virtual sample arrays, progress monitor hooks, BMP/JPEG error codes.
