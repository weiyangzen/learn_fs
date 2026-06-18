# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/wscanf.c

Read completely: 70 lines.

Implements variadic `wscanf()` and `wscanf_l()`. Both collect arguments with `va_start`, delegate to `vfwscanf()` or `vfwscanf_l()` on `stdin`, then return the scanning result.

No parsing logic is local to this file.
