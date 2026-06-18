# File Research: sources/os/bsd/netbsd-src/lib/libc/regex/cname.h

Static table mapping POSIX collating element names to single character codes. It includes control names (`NUL`, `SOH`, `ESC`, etc.), common aliases (`alert`, `tab`, `newline`), punctuation names, digit names, and delimiter variants.

Used by `regcomp.c` when parsing bracket collating elements like `[.name.]` and equivalence classes. The table only maps single-character elements; unknown multi-character names are rejected unless they are a single multibyte character in NLS mode.
