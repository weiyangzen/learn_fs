# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/setlocale_local.h

Read completely: 103 lines.

This header defines libc's private locale state: locale name constants, `_locale_cache_t`, `struct _locale`, category setter function type, declarations for category setlocale functions, cache helpers, and `_current_locale()` in libc builds.

Important interactions: included by most locale implementation files. It exposes `_PathLocale`, `_C_cache`, and `__mb_len_max_runtime`.

Security/reliability notes: no standalone logic beyond `_current_locale`, which returns the mutable global locale in `_LIBC` builds. The fixed `_LOCALENAME_LEN_MAX` shapes storage for category names and composite queries.
