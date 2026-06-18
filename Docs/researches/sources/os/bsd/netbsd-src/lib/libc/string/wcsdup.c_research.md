# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wcsdup.c

Implements `wcsdup()`. It computes `wcslen(str) + 1`, allocates with overflow-safe `reallocarr()`, and copies the wide string including NUL with `wmemcpy()`.

On allocation/overflow error it returns NULL and leaves `errno` set by `reallocarr()` usage.
