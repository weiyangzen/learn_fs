# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/djpeg.c

Command-line JPEG decompressor front end.

Key points:
- Builds an addon message table from `cderror.h`, initializes `jpeg_decompress_struct`, and attaches app-specific message range metadata to the IJG error manager.
- Defines output format enum values for BMP, GIF, OS/2 BMP, PPM/PGM, RLE, Targa, and TIFF placeholder, with `DEFAULT_FMT` defaulting to PPM unless overridden.
- `usage` lists decompression, color quantization, scaling, output format, DCT, dithering, colormap, smoothing, memory, output file, and verbosity switches, feature-gated by compile-time support macros.
- `parse_switches` handles output format selection, color count/quantization, DCT method, dither mode, verbose/debug, fast-mode bundle, grayscale output, external color-map reading, max memory, fancy upsampling suppression, one-pass quantization, output filename, and IDCT scaling.
- Installs custom marker processors for JPEG COM and APP12 markers; `print_text_marker` emits marker text at trace level, escaping nonprintable characters and normalizing CR/LF forms.
- `main` opens input/output, starts optional progress monitoring, sets `jpeg_stdio_src`, reads the JPEG header, reparses real options, initializes the selected destination module, starts decompression, writes the output header, reads scanlines into the destination buffer, emits rows, finishes output/decompression, cleans up, and exits with warning status when appropriate.

Dependencies and interactions:
- Depends on `cdjpeg.h`, `jversion.h`, destination modules (`jinit_write_*`), `read_color_map`, and common helpers from `cdjpeg.c`.
- Uses core IJG APIs including `jpeg_set_marker_processor`, `jpeg_read_header`, `jpeg_start_decompress`, `jpeg_read_scanlines`, and `jpeg_finish_decompress`.

Risk notes:
- The marker printer assumes a non-suspending data source, as stated in comments; it calls `ERREXIT` if suspension would be needed.
- Output format enum includes `FMT_TIFF`, but no TIFF writer is selected in the switch; unsupported/default cases raise `JERR_UNSUPPORTED_FORMAT`.
- Like `cjpeg`, CLI state is global/static and designed for one process invocation, not reentrant embedding.
