# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/localeconv.c

Read completely: 51 lines.

This file implements `localeconv` and `localeconv_l`. The current-locale wrapper delegates to `localeconv_l`, which returns a non-const pointer to the `struct lconv` cached inside `loc->cache`.

Important interactions: cache contents are built by `_setlocale_cache` in `setlocale.c` from monetary and numeric category implementations.

Security/reliability notes: returns internal cache storage with const cast, matching libc API expectations but exposing mutable-looking data backed by shared locale cache.
