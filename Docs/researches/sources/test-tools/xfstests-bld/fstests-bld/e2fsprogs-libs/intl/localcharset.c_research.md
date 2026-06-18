<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/localcharset.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/localcharset.c

## Purpose
This file determines a canonical character set name for the current locale, using platform APIs, environment variables, and `charset.alias` mappings.

## Important APIs, Types, and Functions
The public function is `locale_charset(void)`. Static helper `get_charset_aliases()` lazily reads or constructs alias mappings. Important state is static volatile `charset_aliases`.

## Control Flow
On Unix-like systems, it prefers `nl_langinfo(CODESET)` when available, otherwise falls back to locale environment variables. On Windows it builds `CP<ACP>` from `GetACP`; on OS/2 it uses locale overrides or `DosQueryCp`. It then scans alias pairs from `charset.alias` or built-in VMS/Windows tables, substitutes canonical names, and returns `ASCII` instead of an empty result.

## State and Persistence
The alias table is cached in process memory after first load. It reads `LIBDIR/charset.alias` through `relocate()` when relocatable support is enabled. It does not write files.

## Dependencies and Integration Points
It depends on `localcharset.h`, optional `langinfo.h`, `locale.h`, Windows/OS2 APIs, `relocatable.h`, and `config.charset`-generated `charset.alias`. `loadmsgcat.c` uses `locale_charset()` to choose output conversion when no binding codeset or `OUTPUT_CHARSET` is set.

## Risks
The static cache is only weakly protected with `volatile`, not real locking, so concurrent first-use can race in standalone builds. Missing alias files degrade to raw platform names or ASCII fallback. Environment-derived encodings may be non-canonical until alias mapping succeeds.

## Test Signals
Test with `nl_langinfo`, without `nl_langinfo`, with `LC_ALL`/`LC_CTYPE`/`LANG`, with custom `charset.alias`, missing alias file, Windows/OS2 codepage branches where possible, and empty/unknown codeset fallback.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/localcharset.c -->
