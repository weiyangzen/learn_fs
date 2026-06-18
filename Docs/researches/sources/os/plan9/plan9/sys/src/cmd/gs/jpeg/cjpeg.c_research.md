# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/cjpeg.c

Command-line JPEG compressor front end from the IJG sample applications.

Key behavior:
- Builds an addon message table from `cderror.h`.
- `select_file_type` picks an input reader by first byte or by explicit `-targa`; supports BMP, GIF, PPM/PGM, RLE, and Targa when compiled.
- `usage` prints supported switches based on compiled features.
- `parse_switches` handles compressor options including arithmetic coding, baseline quantizers, DCT method, debug/verbose tracing, grayscale output, max memory, entropy optimization, output filename, progressive mode, quality, quantization-table file, quantization slots, restart intervals, sampling factors, scan scripts, input smoothing, and Targa forcing.
- Delays some option application until image header/color space is known: quality/table processing, qslots, sampling factors, progressive setup, and scan scripts.
- `main` creates a `jpeg_compress_struct`, installs standard errors plus addon messages, optionally enables signal cleanup, sets default compressor parameters, parses filenames, opens binary input/output, initializes progress reporting, selects and starts the source module, updates default colorspace from input, reparses switches for real, starts compression, writes scanlines from the source manager, finishes input/compression, destroys the object, closes files, and exits with warning status if needed.

Dependencies:
- Uses `cdjpeg.h`, `jversion.h`, IJG compressor APIs, format-reader modules, `rdswitch.c` helpers, and optional Macintosh command-line support.
- Uses compile-time feature macros for optional codecs and compressor capabilities.

Research notes:
- The two-pass switch parse is intentional: first pass finds filenames; second pass applies settings after input color space is known.
- File type detection only consumes one byte because portable `ungetc` guarantees only one pushed-back character.
- Unsupported compile-time features fail early with explicit messages.
