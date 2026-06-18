<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/finddomain.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/finddomain.c

## Purpose
This file finds or creates the `loaded_l10nfile` structure for a domain, locale, and directory binding, then triggers catalog loading for the best available fallback candidate.

## Important APIs, Types, and Functions
The main function is `_nl_find_domain(dirname, locale, domainname, domainbinding)`. It owns the static `_nl_loaded_domains` list. It calls `_nl_make_l10nflist`, `_nl_expand_alias`, `_nl_explode_name`, `_nl_load_domain`, and optionally `_nl_unload_domain` in libc cleanup.

## Control Flow
The function first checks whether the exact locale/domain entry is already in `_nl_loaded_domains`; if found, it loads undecided entries and scans successors until a loaded catalog is found. For new locales, it expands aliases, destructively splits locale components, builds a fallback list through `_nl_make_l10nflist`, loads the primary candidate, then walks successors until a catalog with data is available.

## State and Persistence
State persists in the process-global `_nl_loaded_domains` linked list and its successor graph. Loaded catalog data is attached to `loaded_l10nfile->data`.

## Dependencies and Integration Points
It is called by `dcigettext.c` and delegates file creation/path fallback logic to `l10nflist.c` and actual `.mo` loading to `loadmsgcat.c`.

## Risks
The global loaded-domain cache is never freed in standalone builds. Alias expansion can allocate a replacement locale, so cleanup paths must free it correctly. The return logic returns the top-level `retval` even when a successor contains the data, so callers must also check successors as `dcigettext.c` does.

## Test Signals
Test exact cache hits, alias expansion, fallback from specific to generic locale, missing catalogs, and repeated lookups confirming no duplicate loaded-domain entries.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/finddomain.c -->
