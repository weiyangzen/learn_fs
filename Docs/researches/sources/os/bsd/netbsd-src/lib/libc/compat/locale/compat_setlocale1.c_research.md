# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/locale/compat_setlocale1.c

Read completely: 55 lines.

This implements `compat_setlocale`, an old `setlocale` ABI wrapper. It warns on compatibility references, sets `__mb_len_max_runtime` to `1`, then calls the shared `__setlocale(category, locale)` implementation.

Important interactions: used for binaries built against an ABI where `MB_LEN_MAX` behavior was fixed to one byte.

Security/reliability notes: no allocation or parsing here. Correctness depends on callers expecting the historical single-byte runtime maximum.
