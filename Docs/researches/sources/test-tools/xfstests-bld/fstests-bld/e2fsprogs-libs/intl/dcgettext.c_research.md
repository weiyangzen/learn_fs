<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/dcgettext.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/dcgettext.c

## Purpose
This is the `dcgettext` wrapper. It looks up a singular message in a named domain for a caller-provided locale category.

## Important APIs, Types, and Functions
The public function is `DCGETTEXT(domainname, msgid, category)`, mapped to libc or `libintl_dcgettext` names. It delegates to `DCIGETTEXT(domainname, msgid, NULL, 0, 0, category)`.

## Control Flow
There is no local lookup logic. The wrapper passes `plural=0` and no plural fallback to the internal resolver, then returns its result.

## State and Persistence
No local state is stored. It reads all translation state indirectly through `dcigettext.c`.

## Dependencies and Integration Points
It depends on `gettextP.h`, `libgnuintl.h`/`libintl.h`, and `libintl_dcigettext`. It is part of the public gettext API surface exported by the included library.

## Risks
Behavioral risks are inherited from `dcigettext.c`: invalid categories, missing catalogs, cache invalidation, and charset conversion. The wrapper itself has minimal risk.

## Test Signals
Use a fixture domain and category to confirm it returns translated strings when catalogs exist and the original `msgid` when no catalog or entry exists.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/dcgettext.c -->
