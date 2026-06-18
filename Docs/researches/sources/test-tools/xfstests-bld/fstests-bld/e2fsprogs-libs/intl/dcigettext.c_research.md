<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/dcigettext.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/dcigettext.c

## Purpose
This is the central runtime resolver for GNU gettext lookups. It implements domain/category/locale selection, catalog loading, known-translation caching, plural selection, secure-mode filtering, charset conversion lookup, and fallback to untranslated strings.

## Important APIs, Types, and Functions
The exported internal entry is `DCIGETTEXT(domainname, msgid1, msgid2, plural, n, category)`, mapped to `__dcigettext` or `libintl_dcigettext`. Important helpers and data include `struct known_translation_t`, `transcmp`, `_nl_current_default_domain`, `_nl_default_dirname`, `_nl_domain_bindings`, `_nl_find_msg`, `plural_lookup`, `guess_category_value`, `category_to_name`, `_nl_msg_cat_cntr`, `_nl_state_lock`, and optional `tsearch` cache root.

## Control Flow
The resolver rejects `NULL` `msgid1`, substitutes the current default domain when none is provided, checks the known-translation cache, preserves errno, determines secure/SUID mode, finds the domain binding, resolves relative bindings against `getcwd`, determines the locale category name and value, and builds an `LC_CATEGORY/domain.mo` suffix. It iterates colon-separated locale candidates, skipping path-containing locale names in secure mode and returning untranslated strings for `C` or `POSIX`. For each candidate it calls `_nl_find_domain`, then `_nl_find_msg` on the chosen domain and successors. Found translations are cached with the current catalog counter and optionally reduced to the plural variant via `plural_lookup`.

## State and Persistence
Process-global state includes the current default domain, domain bindings, known-translation tree, catalog counter, secure-mode flag, and conversion memory cache. No direct filesystem writes occur; the code reads catalogs through downstream loaders.

## Dependencies and Integration Points
It depends on locale APIs, environment variables `LANGUAGE`, `LC_*`, and `LANG`, filesystem path handling, `_nl_find_domain` in `finddomain.c`, `_nl_find_msg` and catalog structures in `loadmsgcat.c`, plural expression support from `eval-plural.h`, and hash support from `hash-string.h`. It is the target for `gettext`, `dgettext`, `dcgettext`, `ngettext`, `dngettext`, and `dcngettext` wrappers.

## Risks
Standalone locking macros are no-ops, so global caches and bindings are not protected in non-glibc builds. Relative domain directories depend on `getcwd` and can fail back to untranslated text. Secure-mode filtering must remain correct because locale values can otherwise include paths. Cache invalidation relies on `_nl_msg_cat_cntr` and binding `codeset_cntr`. Plural expression division by zero intentionally raises `SIGFPE` on platforms where integer divide-by-zero does not.

## Test Signals
Exercise default and named domains, category-specific lookup, `LANGUAGE` chains, secure-mode path rejection, relative and absolute bind paths, C/POSIX fallback, tsearch cache hits after repeated calls, cache invalidation after rebind, plural lookup bounds, errno preservation, and iconv conversion when a catalog charset differs from output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/dcigettext.c -->
