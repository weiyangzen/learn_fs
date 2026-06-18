# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/freelocale.c

Read completely: 51 lines.

This file implements `freelocale` by asserting the argument is not `LC_GLOBAL_LOCALE`, not `LC_C_LOCALE`, and not NULL, then freeing the locale object.

Important interactions: matches the shallow-allocation model of `newlocale`/`duplocale`; category implementations and caches are shared and not freed here.

Security/reliability notes: misuse is caught only by diagnostic assertions, which may be disabled. Passing special locale objects in release builds would be unsafe.
