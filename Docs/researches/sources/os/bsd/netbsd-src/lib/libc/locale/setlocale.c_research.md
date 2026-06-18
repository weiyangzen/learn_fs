# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/setlocale.c

Read completely: 203 lines.

This file implements libc locale dispatch and cache construction. It registers category handlers, initializes `_PathLocale`, resolves environment defaults, implements `_setlocale_cache`, `_find_category`, `_get_locale_env`, `__setlocale`, and public `setlocale`.

Important interactions: category handlers include generic `LC_ALL`, dummy `LC_COLLATE`, and Citrus category loaders. `_setlocale_cache` deduplicates caches by monetary/numeric/message category names and fills `struct lconv` fields from category implementations.

Security/reliability notes: the cache list is explicitly noted as not locked, leaking memory on races. `__setlocale` calls `_setlocale_cache` even if the category handler returned NULL, and does not free the allocated cache if an existing cache is reused inside `_setlocale_cache` only after the call succeeds. Environment lookup rejects names containing `/`.
