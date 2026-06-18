<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/gettext.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/gettext.c

## Purpose
This wrapper implements the basic `gettext(msgid)` API for the current default domain and `LC_MESSAGES`.

## Important APIs, Types, and Functions
The public entry is `GETTEXT(msgid)`, mapped to libc or `libintl_gettext`. It calls `DCGETTEXT(NULL, msgid, LC_MESSAGES)`.

## Control Flow
The wrapper passes a `NULL` domain to mean "use current default domain" and delegates all lookup work to `dcgettext`/`dcigettext`.

## State and Persistence
No local state. The current default domain is stored in `dcigettext.c` and set by `textdomain.c`.

## Dependencies and Integration Points
It depends on `gettextP.h`, `libgnuintl.h`/`libintl.h`, `LC_MESSAGES`, and `dcgettext`.

## Risks
Behavior depends on current process-global textdomain and locale. The wrapper itself is intentionally thin.

## Test Signals
Set a textdomain and locale, call `gettext`, and verify translated and untranslated fallback behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/gettext.c -->
