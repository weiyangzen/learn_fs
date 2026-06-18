<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/dngettext.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/dngettext.c

## Purpose
This wrapper implements plural lookup for a specified domain using `LC_MESSAGES`.

## Important APIs, Types, and Functions
The public entry is `DNGETTEXT(domainname, msgid1, msgid2, n)`, mapped to libc or `libintl_dngettext`. It calls `DCNGETTEXT(domainname, msgid1, msgid2, n, LC_MESSAGES)`.

## Control Flow
It fixes the category and delegates plural handling to `dcngettext` and ultimately `dcigettext`.

## State and Persistence
No local state is stored.

## Dependencies and Integration Points
It depends on `locale.h`, `gettextP.h`, `libgnuintl.h`/`libintl.h`, and `dcngettext`.

## Risks
The main risk is incorrect plural fallback if catalog plural metadata is missing or malformed; actual behavior is inherited from `dcigettext.c` and `eval-plural.h`.

## Test Signals
Test counts across plural boundaries for a bound domain with a known plural expression, plus missing-catalog fallback for `n == 1` and `n != 1`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/dngettext.c -->
