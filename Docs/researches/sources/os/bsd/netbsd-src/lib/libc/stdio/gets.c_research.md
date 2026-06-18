# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/gets.c

Implements legacy unsafe `gets()` through internal `__gets()`. It locks `stdin`, reads bytes with `getchar_unlocked()` until newline or EOF, NUL-terminates the caller buffer, and returns `NULL` only when EOF occurs before any byte is read.

The file emits a link-time warning that `gets()` is unsafe. There is no bounds check by design, so this is retained only for ABI/API compatibility.
