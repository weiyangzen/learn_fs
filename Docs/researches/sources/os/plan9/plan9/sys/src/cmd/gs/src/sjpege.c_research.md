# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sjpege.c

JPEG encode-side IJG wrapper functions.

Key behavior:
- `gs_jpeg_create_compress` installs error handling, initializes common JPEG stream data, and calls `jpeg_create_compress`.
- Wraps IJG compressor operations for defaults, colorspace, linear quality, quality, start, scanline writing, and finish.
- Every entry point establishes `setjmp` protection and returns Ghostscript error codes on IJG failure.

Notable dependencies:
- Common JPEG wrapper support from `sjpeg.h`/`sjpegc.c`.
- DCT stream state from `sdct.h`.

Research notes:
- This file is strictly a side-effect containment layer for IJG calls; actual stream buffering and DCT behavior live elsewhere.
