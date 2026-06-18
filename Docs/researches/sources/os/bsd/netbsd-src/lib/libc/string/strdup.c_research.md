# File Research: sources/os/bsd/netbsd-src/lib/libc/string/strdup.c

Implements `strdup()`. It allocates `strlen(str) + 1` bytes, copies the complete string including NUL, and returns the new buffer.

Allocation failure returns NULL with `malloc`’s `errno`.
