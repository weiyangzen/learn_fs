# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/ungetwc.c

Implements `ungetwc()`. It rejects `WEOF`, locks the stream, sets wide orientation, obtains the per-stream wide I/O state with `WCIO_GET()`, and pushes the wide character into the fixed wide unget buffer.

It cannot reuse byte `ungetc()` because there is no reverse conversion path for arbitrary wide strings to byte sequences. Buffer exhaustion or allocation failure returns `WEOF`.
