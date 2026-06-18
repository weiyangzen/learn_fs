<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/l10nflist.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/l10nflist.c

## Purpose
This file constructs and caches candidate localized catalog filenames, including fallback successor lists for less-specific locale variants.

## Important APIs, Types, and Functions
Exports are `_nl_make_l10nflist(...)` and `_nl_normalize_codeset(codeset, name_len)`. Helpers include fallback implementations for `__argz_count`, `__argz_stringify`, `__argz_next`, `pop`, and `stpcpy`. It uses `struct loaded_l10nfile` from `loadinfo.h`.

## Control Flow
`_nl_make_l10nflist` builds an absolute or relative candidate path from directory list, locale components, and filename suffix. It searches the sorted cache list for an existing filename. If allocation is requested and no entry exists, it allocates a `loaded_l10nfile`, inserts it, marks some synthetic entries as already decided, and recursively builds successors by dropping locale mask bits and iterating directory-list elements. `_nl_normalize_codeset` lowercases alphanumeric codeset names and prefixes digit-only names with `iso`.

## State and Persistence
State persists in the caller-provided `l10nfile_list`. Each entry owns an allocated filename and successor pointers. There is no filesystem write.

## Dependencies and Integration Points
It is used by `finddomain.c` to build the catalog fallback graph. It depends on locale mask semantics from `loadinfo.h` and argz-like handling for directory lists.

## Risks
The recursive successor construction can allocate many entries for complex masks and multi-directory paths. It stores entries in sorted order but relies on string comparison direction matching callers. Locale fallback order is encoded in mask iteration and comments, so subtle changes can alter translation precedence.

## Test Signals
Test filename generation for XPG and CEN locale parts, multi-directory alias paths, absolute language paths, normalized versus original codesets, and fallback successor ordering.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/l10nflist.c -->
