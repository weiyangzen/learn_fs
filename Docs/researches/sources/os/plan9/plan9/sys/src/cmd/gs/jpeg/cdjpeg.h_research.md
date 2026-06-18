# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/cdjpeg.h

Shared declarations for IJG sample applications `cjpeg` and `djpeg`; not used by the core JPEG library.

Key behavior:
- Defines `JPEG_CJPEG_DJPEG` and `JPEG_INTERNAL_OPTIONS` before including IJG headers so application feature switches are visible.
- Declares the `cjpeg_source_struct` source-module interface: `start_input`, `get_pixel_rows`, `finish_input`, input `FILE`, row buffer, and buffer height.
- Declares the `djpeg_dest_struct` output-module interface: `start_output`, `put_pixel_rows`, `finish_output`, output `FILE`, row buffer, and buffer height.
- Defines `cdjpeg_progress_mgr`, extending `jpeg_progress_mgr` with extra pass accounting and cached percentage.
- Provides short external-name mappings under `NEED_SHORT_EXTERNAL_NAMES`.
- Declares image module factories for BMP, GIF, PPM, RLE, and Targa readers/writers.
- Declares cjpeg option helpers from `rdswitch.c`, djpeg color map helper from `rdcolmap.c`, common helpers from `cdjpeg.c`, and binary `fopen` mode macros.
- Defines portable exit codes, including VMS-specific success/warning behavior.

Dependencies:
- Includes `jinclude.h`, `jpeglib.h`, `jerror.h`, and `cderror.h`.
- Depends on the rest of the IJG application modules to implement the declared factories/helpers.

Research notes:
- This is the application-module contract for file format adapters.
- It exposes internal option macros because the command-line tools need to know which optional formats/features were compiled.
