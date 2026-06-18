# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsiodevs.c

## Role

`gsiodevs.c` implements `%stdin%`, `%stdout%`, and `%stderr%` IODevices for non-PostScript configurations.

This is standard-stream IODevice adapter code, not filesystem code.

## Main Interfaces

- Defines `gs_iodev_stdin`, `gs_iodev_stdout`, and `gs_iodev_stderr`.
- Internal helpers: `stdio_close_file`, `stdio_open`, `stdin_open`, `stdout_open`, `stderr_open`.

## Core Behavior

- Opens Ghostscript streams around `mem->gs_lib_ctx->fstdin`, `fstdout`, or `fstderr` using a 128-byte allocated buffer.
- Allows only the expected access mode: read for `%stdin%`, write for `%stdout%` and `%stderr%`.
- The close proc frees the stream buffer but intentionally does not close the underlying stdio file.

## Notable Risks

If `s_alloc` succeeds but buffer allocation fails, cleanup frees both pointers. The underlying standard file pointers are trusted to be valid in the library context.
