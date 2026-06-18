# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/cjpeg.c

Command-line JPEG compressor front end.

Key points:
- Creates an app-specific message table from `cderror.h`, initializes `jpeg_compress_struct`, attaches the message table, and uses IJG default error handling.
- `select_file_type` detects input format from the first byte, constrained by portable `ungetc` behavior; Targa can be forced with `-targa` because not all Targa files are first-byte-identifiable.
- `usage` lists baseline and advanced switches, feature-gated by compile-time support for entropy optimization, progressive mode, arithmetic coding, DCT methods, smoothing, multiscan scripts, and Targa.
- `parse_switches` handles quality, grayscale, DCT method, restart intervals, smoothing, max memory, output filename, verbose/debug, arithmetic coding, baseline quantization, external quantization tables, quantization slots, sampling factors, progressive mode, scan scripts, optimization, and Targa forcing.
- Parsing runs twice: a first pass finds file names before the source format is known, and a second real pass after input header parsing applies colorspace-dependent defaults and delayed options.
- `main` opens input/output according to Unix or two-file command-line style, starts optional progress monitoring, initializes the selected source module, calls `jpeg_default_colorspace`, sets `jpeg_stdio_dest`, starts compression, repeatedly pulls source pixel rows and writes scanlines, then finishes and cleans up.

Dependencies and interactions:
- Depends on `cdjpeg.h`, `jversion.h`, source modules (`jinit_read_*`), switch helpers (`read_quant_tables`, `read_scan_script`, `set_quant_slots`, `set_sample_factors`), and common helpers from `cdjpeg.c`.
- Format support is selected by `BMP_SUPPORTED`, `GIF_SUPPORTED`, `PPM_SUPPORTED`, `RLE_SUPPORTED`, and `TARGA_SUPPORTED`.

Risk notes:
- Input auto-detection only examines one byte, so unsupported or ambiguous formats depend on explicit user switches.
- Command-line parsing uses global `outfilename` and `is_targa`; this is suitable for process-level CLI use, not reentrant library embedding.
- Options that allocate/read external files are deliberately delayed; changes to parsing order must preserve that two-pass design.
