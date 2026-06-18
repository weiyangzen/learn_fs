# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lc_time.c

Locale loader for `LC_TIME`.

Key behavior:
- Defines a large key table for abbreviated/full weekday names, abbreviated/full month names, AM/PM strings, and date/time format strings.
- Normal DB initialization reads each string by symbol from Citrus DB and duplicates it into `_TimeLocale`.
- Fallback initialization reads values line-by-line in the same key order.
- Uninit frees every allocated string slot.
- Category DB path is `LC_TIME`; magic is `CtrsTI10`.

This loader is data-table driven and relies on `nb_lc_time_misc.h` index macros for field placement.
