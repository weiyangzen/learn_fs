# File Research: sources/os/bsd/netbsd-src/lib/libc/string/strtok_r.c

Implements `strtok_r()`. It skips leading delimiter characters, returns NULL when no token remains, scans until the next delimiter or NUL, writes a NUL terminator for non-final tokens, and stores continuation state in `*lasts`.

Delimiter membership is checked by simple nested loops.
