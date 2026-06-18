<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/dgettext.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/dgettext.c

## Purpose
This wrapper implements singular lookup for a specified domain using the `LC_MESSAGES` category.

## Important APIs, Types, and Functions
The public entry is `DGETTEXT(domainname, msgid)`, mapped to libc or `libintl_dgettext`. It calls `DCGETTEXT(domainname, msgid, LC_MESSAGES)`.

## Control Flow
The wrapper simply fixes the category to `LC_MESSAGES` and delegates to `dcgettext`.

## State and Persistence
No local state is stored. All binding, cache, and catalog state lives in shared gettext internals.

## Dependencies and Integration Points
It depends on `locale.h`, `gettextP.h`, `libgnuintl.h`/`libintl.h`, and `dcgettext`.

## Risks
The wrapper depends on `LC_MESSAGES` availability or a configured fallback in the public header. Otherwise risks are inherited from the central resolver.

## Test Signals
Bind a test domain and locale, call `dgettext`, and confirm `LC_MESSAGES` catalogs are searched rather than other categories.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/dgettext.c -->
