# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/djpeg.c

Command-line JPEG decompressor front end from the IJG sample applications.

Key behavior:
- Builds an addon message table from `cderror.h`.
- Defines output format enum values for BMP, GIF, OS/2 BMP, PPM/PGM, RLE, Targa, and TIFF placeholder, with `DEFAULT_FMT` defaulting to PPM.
- `usage` prints decompression/output switches based on compiled capabilities.
- `parse_switches` handles output format selection, color quantization, IDCT method, dithering, debug/verbose tracing, fast mode, grayscale output, external color map loading, max memory, fancy upsampling suppression, one-pass quantization, output filename, and scaling.
- `jpeg_getc` reads marker bytes from the JPEG source manager and rejects suspension.
- `print_text_marker` replaces selected marker processors to print COM and APP12 marker payloads as readable text when tracing is enabled.
- `main` creates a decompressor, installs standard and addon errors, installs COM/APP12 marker processors, optionally enables signal cleanup, parses filenames, opens binary input/output, starts progress reporting, reads JPEG headers, reparses switches for real, chooses an output destination module, starts decompression, streams scanlines into the output module, finishes output/decompression in the correct memory-lifetime order, destroys the object, closes files, and exits with warning status if needed.

Dependencies:
- Uses `cdjpeg.h`, `jversion.h`, ctype, IJG decompressor APIs, destination modules, `rdcolmap.c`, and optional Macintosh command-line support.
- Compile-time feature macros determine available output modules and options.

Research notes:
- Like `cjpeg`, switch parsing is split so file handling and trace level are available before full parameter application.
- Marker printing relies on a non-suspending data source.
- Output module initialization occurs after option parsing and before `jpeg_start_decompress` so format modules can force crucial settings such as quantization.
