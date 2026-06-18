# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/getdelim.c

Implements `__getdelim()` and public `getdelim()`. The internal routine reads from a byte-oriented stream until a separator or EOF, grows the caller-provided buffer with power-of-two sizing, copies directly from the stream buffer, appends a NUL byte, and returns the byte count.

Important behavior: null `buf`/`buflen` arguments set `EINVAL`; length overflow or `SSIZE_MAX` overflow sets `EOVERFLOW`; stream errors mark `__SERR`. Public `getdelim()` only adds stream locking around `__getdelim()`.
