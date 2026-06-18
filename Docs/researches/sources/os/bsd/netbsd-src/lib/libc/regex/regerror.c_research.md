# File Research: sources/os/bsd/netbsd-src/lib/libc/regex/regerror.c

Implements `regerror()`, mapping regex error codes to human-readable messages or symbolic names. It supports NetBSD extensions `REG_ATOI` and `REG_ITOA` for converting between names and numbers.

The static `rerrs[]` table covers standard errors such as `REG_NOMATCH`, `REG_BADPAT`, `REG_EBRACK`, `REG_ESPACE`, `REG_INVARG`, and `REG_ILLSEQ`. `regerror()` returns the required buffer length including NUL and copies with `strlcpy()` when a destination buffer is supplied.
