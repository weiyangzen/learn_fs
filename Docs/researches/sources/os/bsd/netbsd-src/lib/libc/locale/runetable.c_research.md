# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/runetable.c

Read completely: 353 lines.

This file defines `_DefaultRuneLocale`, the built-in C/POSIX rune classification and mapping table. It includes cached runetype bits for byte values, lower/upper mapping arrays, empty extended ranges, codeset `"646"`, the default Citrus ctype, translation entries, classification entries, and byte ctype/toupper/tolower table pointers.

Important interactions: global C locale objects in `global_locale.c` point to this default rune locale. `rune.c` copies pieces of this table when initializing dynamically loaded rune locales.

Security/reliability notes: static data only. Correctness is foundational for all C-locale ctype and wide classification behavior.
