# File Research: sources/os/bsd/netbsd-src/lib/libc/string/stresep.c

Implements `stresep(char **stringp, const char *delim, int esc)`, an escaped variant of `strsep()`. It returns possibly-empty tokens separated by delimiter characters, writes NUL terminators into the input string, and updates `*stringp`.

When `esc` is nonzero and encountered, it removes the escape byte with `memmove()` so the following character is treated literally rather than as a delimiter.
