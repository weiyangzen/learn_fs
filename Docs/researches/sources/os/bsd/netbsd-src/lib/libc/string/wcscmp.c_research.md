# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wcscmp.c

Implements `wcscmp()`. It advances while characters are equal, returns zero at matching NUL termination, otherwise returns the difference between the first unequal wide characters cast through `__nbrune_t`.

The code notes an assumption about `wchar_t` representation.
