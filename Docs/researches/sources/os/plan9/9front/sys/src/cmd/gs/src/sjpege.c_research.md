# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sjpege.c

Implements IJG libjpeg encode wrapper functions.

Key points:
- `gs_jpeg_create_compress` installs Ghostscript error handling, initializes common JPEG stream data, and calls `jpeg_create_compress`.
- Wraps IJG defaults, colorspace selection, linear quality, normal quality, start compression, scanline write, and finish compression operations.
- Each wrapper establishes the JPEG error `setjmp` context and returns Ghostscript error codes on libjpeg error exits.

Research relevance:
- Encode-side call adapter for Ghostscript DCTEncode streams.
