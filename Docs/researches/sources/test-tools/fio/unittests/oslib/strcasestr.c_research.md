# sources/test-tools/fio/unittests/oslib/strcasestr.c

Purpose: CUnit tests for either fio's fallback `strcasestr()` or the platform implementation, depending on `CONFIG_STRCASESTR`.

Important APIs/functions: three tests cover numeric haystacks, uppercase haystacks, and mixed-case needles. They assert matches at the start, matches at offset one, no match when needle is longer/nonmatching, and empty needle returning the haystack pointer.

Control flow/state: all tests use string literals and compare returned pointers directly against expected offsets.

Dependencies/integration: includes `../../oslib/strcasestr.h` when the platform lacks `strcasestr`; otherwise includes `<string.h>`. Registered by `fio_unittest_oslib_strcasestr()`.

Risks/test signals: tests encode GNU/BSD empty-needle behavior and case-insensitive semantics. Missing cases include NULL handling, locale-sensitive characters, repeated partial matches, and non-ASCII behavior.
