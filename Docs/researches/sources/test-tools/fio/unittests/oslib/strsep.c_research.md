# sources/test-tools/fio/unittests/oslib/strsep.c

Purpose: CUnit tests for fallback or platform `strsep()`.

Important APIs/functions: `test_strsep_1()` checks NULL `*stringp` returns NULL. `test_strsep_2()` verifies no-delimiter cases return the whole string and set `stringp` NULL. `test_strsep_3()` uses delimiters `"ABC"` against `"ABCDEFG"` to verify delimiter overwrite with NUL and pointer advancement through consecutive delimiters.

Control flow/state: mutable stack strings are modified in place, matching `strsep()` semantics. Returned token pointers and updated `string` values are asserted after each call.

Dependencies/integration: includes `../../oslib/strsep.h` unless `CONFIG_STRSEP` selects libc.

Risks/test signals: good coverage for NULL, empty delimiter, no delimiter, and delimiter overwrite behavior. Missing cases include repeated delimiters in the middle, trailing delimiters, and multi-character delimiter sets beyond first-character positions.
