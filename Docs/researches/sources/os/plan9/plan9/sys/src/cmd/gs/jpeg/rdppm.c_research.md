# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/rdppm.c

IJG `cjpeg` source adapter for PPM/PGM input, compiled only under `PPM_SUPPORTED`.

Key behavior:

- Parses PBMPLUS-style PGM/PPM headers for text P2/P3 and raw P5/P6 formats, with comment skipping via `pbm_getc()`.
- Rejects PBM and malformed headers, then fills `j_compress_ptr` input geometry, component count, color space, and precision.
- Provides row readers for text gray/RGB, raw byte gray/RGB with rescaling, direct raw-byte rows when `maxval == MAXJSAMPLE`, and nonstandard 2-byte-per-sample raw formats.
- Allocates a one-row physical I/O buffer for raw formats and a libjpeg sample row unless raw bytes can be read directly into the compressor buffer.
- Builds a `rescale` lookup table when input `maxval` differs from the JPEG sample range.

The data path is entirely stdio-to-libjpeg: `jinit_read_ppm()` creates the `cjpeg_source_struct`, `start_input_ppm()` selects the row-reader, and each `get_*_row()` returns one decompressor input row. It has no Plan 9 filesystem-specific logic beyond ordinary `FILE *` reads.
