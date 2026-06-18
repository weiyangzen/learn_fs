# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/vasprintf.c

Implements `vasprintf_l()`, `vasprintf()`, `asprintf_l()`, and `asprintf()`. `vasprintf_l()` creates a string-output `FILE` with `__SWR | __SSTR | __SALC`, starts with a 128-byte malloc buffer, formats through `__vfprintf_unlocked_l()`, NUL-terminates, then shrinks the allocation to `ret + 1`.

On allocation or formatting failure it frees the buffer, sets `*str = NULL`, sets `errno = ENOMEM`, and returns `-1`. The non-locale variants use `_current_locale()`.
