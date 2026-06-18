# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/newlocale.c

Read completely: 110 lines.

This file implements `newlocale`. It allocates a new locale object, copies either the source locale or current locale, applies a single locale name or slash-separated names to the categories selected by `mask`, then builds/attaches a locale cache.

Important interactions: uses `_find_category` to call each category's setlocale handler and `_setlocale_cache` to populate `struct lconv` cache data.

Security/reliability notes: if a category handler fails, this implementation does not check each handler return in the single-name path before continuing. It frees the destination on malformed slash strings or cache failure.
