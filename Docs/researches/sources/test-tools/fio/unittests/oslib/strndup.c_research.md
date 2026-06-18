# sources/test-tools/fio/unittests/oslib/strndup.c

Purpose: CUnit tests for fallback or platform `strndup()`.

Important APIs/functions: tests duplicate `"test"` with lengths 3, 4, and 5, expecting truncation to `"tes"`, exact copy, and copy limited by source NUL respectively. `fio_unittest_oslib_strndup()` registers the suite.

Control flow/state: each test allocates with `strndup()` and only asserts if the pointer is non-NULL. The allocated buffers are not freed, which is acceptable for short test execution but not leak-clean.

Dependencies/integration: includes `../../oslib/strndup.h` unless `CONFIG_HAVE_STRNDUP` selects libc.

Risks/test signals: validates NUL-termination and length limiting. Missing cases include zero length, allocation failure behavior, embedded NULs, and freeing in tests to satisfy leak checkers.
