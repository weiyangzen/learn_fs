# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sjpegd.c

JPEG decode-side IJG wrapper functions.

Key behavior:
- `gs_jpeg_create_decompress` installs error handling, initializes common JPEG stream data, and calls `jpeg_create_decompress`.
- `gs_jpeg_read_header`, `gs_jpeg_start_decompress`, `gs_jpeg_read_scanlines`, and `gs_jpeg_finish_decompress` wrap their IJG counterparts in `setjmp` protection.
- Handles IJG version difference where `jpeg_start_decompress` did not return a value in version 5.

Notable dependencies:
- Common JPEG wrapper support from `sjpeg.h`/`sjpegc.c`.
- DCT stream state from `sdct.h`.

Research notes:
- This file contains no decompression logic itself; it is an error-translation boundary around libjpeg.
