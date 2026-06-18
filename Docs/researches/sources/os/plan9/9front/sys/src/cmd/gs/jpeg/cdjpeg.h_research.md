# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/cdjpeg.h

Shared declarations for IJG sample applications `cjpeg` and `djpeg`.

Key points:
- Defines `JPEG_CJPEG_DJPEG` and `JPEG_INTERNAL_OPTIONS` before including `jinclude.h`, `jpeglib.h`, `jerror.h`, and `cderror.h`, enabling app-specific feature macros and internal options.
- Declares the `cjpeg_source_struct` input-module interface: `start_input`, `get_pixel_rows`, `finish_input`, input file, row buffer, and buffer height.
- Declares the `djpeg_dest_struct` output-module interface: `start_output`, `put_pixel_rows`, `finish_output`, output file, row buffer, and buffer height.
- Defines `cdjpeg_progress_mgr`, extending `jpeg_progress_mgr` with extra pass counts and cached printed percent.
- Provides short external-name aliases under `NEED_SHORT_EXTERNAL_NAMES` for systems with limited linker symbol length.
- Declares module factories for BMP, GIF, PPM/PGM, RLE, and Targa readers/writers.
- Declares command support routines from `rdswitch.c`, color-map reading from `rdcolmap.c`, and common helpers from `cdjpeg.c`.
- Defines portable `READ_BINARY`, `WRITE_BINARY`, and exit-code macros.

Dependencies and interactions:
- This is the interface contract between `cjpeg.c`/`djpeg.c` and format-specific modules such as `rdbmp.c`, `rdppm.c`, `wrgif.c`, and `wrbmp.c`.
- Compile-time feature macros in `jconfig.h` decide which declared factories are actually available.

Risk notes:
- The header intentionally exposes internal JPEG options to applications; it is not part of the stable core library API.
- Factory declarations are unconditional, but callers guard use by feature macros; inconsistent `jconfig.h` settings can produce link failures.
