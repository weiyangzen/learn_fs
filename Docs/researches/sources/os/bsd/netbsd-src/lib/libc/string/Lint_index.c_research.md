# File Research: sources/os/bsd/netbsd-src/lib/libc/string/Lint_index.c

Lint stub for legacy `index()`. It declares the string-search prototype and returns NULL.

The actual implementation is provided by the `strchr.c` inclusion wrapper.
