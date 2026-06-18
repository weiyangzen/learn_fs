# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/ungetc.c

Implements `ungetc()`, including dynamic ungetc-buffer growth via `__submore()`. It rejects `EOF`, initializes stdio, locks the stream, sets byte orientation, switches read/write streams into read mode if needed, clears EOF, and either backs up over an identical byte in the normal buffer or creates/extends a separate stack-style ungetc buffer.

The reserve buffer starts in `fp->_ubuf`; when it overflows, the code allocates `BUFSIZ`, then doubles with `realloc()` while keeping pushed-back bytes at the end of the buffer.
