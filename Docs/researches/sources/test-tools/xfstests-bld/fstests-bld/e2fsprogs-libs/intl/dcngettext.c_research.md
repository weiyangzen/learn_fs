<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/dcngettext.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/dcngettext.c

## Purpose
This wrapper implements plural lookup for a specified domain and locale category.

## Important APIs, Types, and Functions
The public entry is `DCNGETTEXT(domainname, msgid1, msgid2, n, category)`, mapped to libc or `libintl_dcngettext`. It delegates to `DCIGETTEXT(domainname, msgid1, msgid2, 1, n, category)`.

## Control Flow
The wrapper marks the lookup as plural and forwards both singular/plural fallback strings plus the count to the central resolver. All catalog search and plural expression evaluation happens in `dcigettext.c`.

## State and Persistence
No local state; it uses the resolver's global state and loaded catalogs.

## Dependencies and Integration Points
It depends on `gettextP.h`, public libintl headers, and `libintl_dcigettext`. `dngettext` delegates to this wrapper with `LC_MESSAGES`.

## Risks
Risks are inherited from plural metadata in catalogs and `plural_lookup`. If no catalog entry exists, fallback uses the Germanic rule `n == 1 ? msgid1 : msgid2`.

## Test Signals
Test with a plural-capable catalog, out-of-range plural expressions, missing translations, and non-`LC_MESSAGES` categories.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/dcngettext.c -->
