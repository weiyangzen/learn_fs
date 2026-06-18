# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/strtonum.c

Implements OpenBSD-compatible `strtonum()`. It delegates parsing and range checking to `strtoi(nptr, &eptr, 10, minval, maxval, &e)`, returns the parsed value on success, and maps errors to `"invalid"`, `"too small"`, or `"too large"` through `errstr`.

It treats `minval > maxval`, syntax errors, trailing junk, unsupported states, and canceled parsing as `"invalid"`.
