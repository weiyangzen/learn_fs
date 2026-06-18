# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuid_compare.3.in

Purpose: manpage template for `uuid_compare()`, documenting lexicographic UUID comparison.

Important APIs, types, and functions: documents `int uuid_compare(uuid_t uu1, uuid_t uu2)`, returning less than, equal to, or greater than zero.

Control flow: documentation only. The text is structured as NAME, SYNOPSIS, DESCRIPTION, RETURN VALUE, AUTHOR, AVAILABILITY, and SEE ALSO.

State and persistence: installed documentation only. The described function reads two UUID buffers and returns comparison status.

Dependencies and integration points: must stay aligned with `uuid.h.in` and the actual comparison implementation. `tst_uuid.c` uses `uuid_compare()` after parse and copy operations.

Risks: the manpage says "lexigraphically", a typo for lexicographically. More importantly, if implementation uses `memcmp()` byte ordering, docs should continue to describe bytewise lexical ordering rather than UUID semantic timestamp ordering.

Test signals: compare equal buffers, copied buffers, and ordered known byte arrays. Build substitution should fill version/date placeholders.
