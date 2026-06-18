# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/example.c

Illustrative skeleton for embedding the IJG JPEG library in an application.

Key points:
- Shows a compression routine, `write_JPEG_file`, that uses external RGB image globals, opens a binary output stream, initializes `jpeg_compress_struct` with standard error handling, sets image dimensions/components/colorspace, applies default compression parameters, sets quality, starts compression, writes scanlines top-to-bottom, finishes, closes, and destroys the JPEG object.
- Documents required input pixel layout: row-major `JSAMPLE` arrays with adjacent component samples, e.g. RGB triplets.
- Explains compressor state variables, partial scanline return semantics, temporary-file use for full-image buffering modes, signal-handler considerations, and top-to-bottom scanline ordering.
- Defines a custom error manager (`my_error_mgr`) embedding `jpeg_error_mgr` plus `jmp_buf`.
- `my_error_exit` calls the standard output-message hook and uses `longjmp` to return control to the caller instead of exiting.
- `read_JPEG_file` demonstrates decompression with setjmp-based recovery: opens input, initializes decompressor, sets stdio source, reads header, starts decompression, allocates a one-scanline buffer via the JPEG memory manager, reads scanlines, passes them to an application-provided sink, finishes, destroys, closes, and reports success/failure.
- Notes that the sample intentionally omits useful application behavior and should be read with `libjpeg.doc`.

Dependencies and interactions:
- Includes `stdio.h`, `jpeglib.h`, and `setjmp.h`.
- References application-provided symbols `image_buffer`, `image_height`, `image_width`, and `put_scanline_someplace`.
- Demonstrates public libjpeg APIs rather than Ghostscript-specific wrappers.

Risk notes:
- It is sample code, not directly runnable; required external image storage and output sink are undeclared implementations.
- The decompression buffer allocation after `jpeg_start_decompress` is acknowledged as slightly outside ideal memory-accounting practice; robust code can call `jpeg_calc_output_dimensions` earlier.
- The custom error path must destroy the JPEG object and close the file after `longjmp`; callers adapting this pattern must keep object/error lifetimes aligned.
