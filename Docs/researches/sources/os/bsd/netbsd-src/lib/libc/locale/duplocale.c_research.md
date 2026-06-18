# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/duplocale.c

Read completely: 52 lines.

This file implements `duplocale` by allocating a new `struct _locale` and shallow-copying the source locale.

Important interactions: shares category implementation pointers and cache pointers with the source. `freelocale` later frees only the locale struct, not the pointed-to shared category data.

Security/reliability notes: there is no explicit NULL or special-locale validation here; callers must pass a valid `locale_t`. Shallow copying is consistent with the cache model but makes ownership shared.
