# File Research: sources/os/bsd/netbsd-src/lib/libc/resolv/herror.c

Implements legacy host lookup error reporting. It defines `h_errlist[]`, `h_nerr`, optional global `h_errno`, `herror()`, and `hstrerror()`.

`herror()` writes an optional prefix, `": "`, the string for current `*__h_errno()`, and newline to standard error using `writev()`. `hstrerror()` maps negative values to “Resolver internal error”, in-range values to `h_errlist`, and others to “Unknown resolver error”.

This is compatibility API around resolver/host lookup errors.
