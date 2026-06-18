# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wcspbrk.c

Implements `wcspbrk(s, set)`, returning the first character in `s` that appears in `set`. It fast-paths empty and single-character sets, then uses the shared wide-character Bloom filter before exact set confirmation.

Returns NULL when no character matches.
