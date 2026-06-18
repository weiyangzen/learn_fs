# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/nb_lc_template.h

Read completely: 244 lines.

This template implements caching and loading for NetBSD locale categories. It defines a per-category cache of loaded parts, optionally guarded by a mutex, loads C/POSIX directly from `_lc_C_locale`, loads other names via `_PREFIX(create_impl)`, handles force mappings, resolves aliases through `locale.alias`, and provides a generated category `setlocale`.

Important interactions: category-specific files define `_PREFIX`, `_CATEGORY_TYPE`, `_CATEGORY_ID`, and `_CATEGORY_NAME` before including it. It depends on `aliasname_local.h`, `_PathLocale`, `_lc_C_locale`, and category-specific `create_impl` functions.

Security/reliability notes: cache entries are intentionally process-lifetime allocations. Alias resolution and file loading are mutex-protected when `_REENTRANT`. The alias macro's force logic is subtle and depends on `/FORCE` semantics.
