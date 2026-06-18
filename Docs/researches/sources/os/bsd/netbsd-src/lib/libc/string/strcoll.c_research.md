# File Research: sources/os/bsd/netbsd-src/lib/libc/string/strcoll.c

Implements `strcoll()` and `strcoll_l()`. Since LC_COLLATE is marked unimplemented here, locale-aware collation reduces to plain `strcmp()`.

`strcoll()` delegates to `strcoll_l()` with the current locale; the locale argument is otherwise ignored.
