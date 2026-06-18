# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sfxfd.c

Implements file streams using direct OS file descriptor calls while retaining `FILE *` at the interface.

Key points:
- Provides read, write, append, seek, flush, close, available, process, and read/write switching procedures.
- Detects seekability with `lseek` and sets stream modes accordingly.
- `sread_subfile` confines reads to a seekable subrange when this file is not included through `sfxboth.c`.
- Read and write process functions call `read(2)`/`write(2)`, retry on `EINTR`, `EAGAIN`, or `EWOULDBLOCK`, and run `process_interrupts`.
- Writing flushes buffered stream data and calls `fsync`, discarding the `fsync` result.
- Switching between reading and writing preserves logical position and append-mode metadata while reinitializing stream procedures.

Dependencies and interactions:
- Mirrors the `sfxstdio.c` public interface.
- Uses `stream.h`, `strimpl.h`, platform wrappers, and debug logging.

Research relevance:
- This is the lower-level Unix-like file I/O backend for Ghostscript streams.
