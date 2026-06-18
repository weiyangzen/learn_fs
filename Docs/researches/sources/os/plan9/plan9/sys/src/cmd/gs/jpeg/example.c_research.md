# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/example.c

Documentation-style sample code showing how to embed the IJG JPEG library for compression and decompression.

Key behavior:
- Declares external application image inputs `image_buffer`, `image_height`, and `image_width`.
- `write_JPEG_file` demonstrates compression setup: standard error manager, `jpeg_create_compress`, stdio destination, image dimensions/components/colorspace, defaults, quality setting, `jpeg_start_compress`, one-row-at-a-time `jpeg_write_scanlines`, `jpeg_finish_compress`, file close, and `jpeg_destroy_compress`.
- Defines `my_error_mgr`, extending `jpeg_error_mgr` with a `jmp_buf`.
- `my_error_exit` overrides fatal error handling by printing the message then `longjmp`ing to caller-controlled cleanup.
- `read_JPEG_file` demonstrates decompression with error recovery: open input first, install custom error manager, establish `setjmp`, create decompressor, stdio source, read header, start decompression, allocate a one-row sample array from the JPEG memory manager, read scanlines, pass rows to application hook `put_scanline_someplace`, finish, destroy, close, and return success/failure.

Dependencies:
- Uses stdio, setjmp, and `jpeglib.h`.
- References external application data and a placeholder output hook `put_scanline_someplace`.

Research notes:
- This file is not intended to be a standalone program.
- It intentionally shows a minimal compressor path and a more robust decompressor path with fatal-error recovery.
- Comments call out important API contracts: set error manager before object creation, keep error manager lifetime tied to JPEG object, use binary file mode where required, and destroy JPEG objects on errors.
