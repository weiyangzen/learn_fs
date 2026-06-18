# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdatadst.c

Stdio destination manager for JPEG compression.

Key behavior:
- Wraps an application-provided `FILE *` with a `jpeg_destination_mgr`.
- Allocates a 4096-byte output buffer in the image pool at compression start.
- Writes full buffers with `JFWRITE`, resets destination pointers, and always reports successful buffer emptying unless a file error occurs.
- Flushes the partial final buffer in `term_destination`, calls `fflush`, and checks `ferror`.
- `jpeg_stdio_dest` allocates the destination manager in the permanent pool so one JPEG object can write multiple images to the same stream.

Dependencies:
- Uses C stdio through IJG `JFWRITE` and JPEG memory/error manager interfaces.

Notable risks:
- This manager does not implement suspension; file-write failures raise fatal JPEG errors.
- The caller remains responsible for opening and closing the stream.
- Reusing a JPEG object with a different destination manager can be unsafe because the permanent private object size may differ.
