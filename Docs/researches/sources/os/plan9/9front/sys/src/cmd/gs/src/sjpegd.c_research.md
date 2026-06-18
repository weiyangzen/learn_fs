# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sjpegd.c

Implements IJG libjpeg decode wrapper functions.

Key points:
- `gs_jpeg_create_decompress` installs Ghostscript error handling, initializes common JPEG stream data, and calls `jpeg_create_decompress`.
- `gs_jpeg_read_header`, `gs_jpeg_start_decompress`, `gs_jpeg_read_scanlines`, and `gs_jpeg_finish_decompress` wrap corresponding IJG calls in `setjmp` protection.
- Handles IJG version differences where older `jpeg_start_decompress` had no return value.
- Errors are converted through `gs_jpeg_log_error`.

Research relevance:
- Decode-side call adapter for Ghostscript DCTDecode streams.
