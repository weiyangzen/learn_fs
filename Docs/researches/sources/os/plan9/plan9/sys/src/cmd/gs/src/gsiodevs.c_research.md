# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsiodevs.c

Implements `%stdin%`, `%stdout%`, and `%stderr%` IODevices for non-PostScript configurations.

Key behavior:
- Defines special IODevice descriptors using `iodev_stdio`.
- `stdio_open` validates access mode, allocates a stream and 128-byte buffer, and binds it to `mem->gs_lib_ctx` stdio handles.
- `stdio_close_file` does not close the underlying stdio file; it only releases the stream buffer.

Devices:
- `%stdin%`: read-only stream from `fstdin`.
- `%stdout%`: write-only stream to `fstdout`.
- `%stderr%`: write-only stream to `fstderr`.

This file keeps standard streams within Ghostscript’s stream abstraction.
