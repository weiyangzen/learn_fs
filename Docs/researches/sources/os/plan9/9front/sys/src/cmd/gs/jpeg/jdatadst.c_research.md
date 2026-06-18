# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdatadst.c

Standard stdio destination manager for JPEG compression output.

Key points:
- Defines a permanent destination manager wrapping a caller-owned `FILE *` and an image-pool 4096-byte output buffer.
- `init_destination` allocates the buffer and initializes `next_output_byte`/`free_in_buffer`.
- `empty_output_buffer` writes the full buffer with `JFWRITE`, resets pointers, and always returns `TRUE`.
- `term_destination` writes remaining buffered bytes, flushes the stream, and checks `ferror`.
- `jpeg_stdio_dest` allocates the destination manager on first use, installs method pointers, and records the output stream.

Dependencies and interactions:
- Used by applications before `jpeg_start_compress` or `jpeg_write_tables`.
- Not a core internal module; includes `jinclude.h`, `jpeglib.h`, and `jerror.h` without defining `JPEG_INTERNALS`.

Risk notes:
- This destination manager does not support output suspension.
- The application remains responsible for opening and closing the `FILE *`.
- Reusing the same compression object with a different destination manager type can be unsafe because the permanent private object size may differ.
