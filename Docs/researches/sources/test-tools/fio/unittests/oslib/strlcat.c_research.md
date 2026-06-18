# sources/test-tools/fio/unittests/oslib/strlcat.c

Purpose: CUnit tests for fio's fallback or platform `strlcat()`.

Important APIs/functions: `test_strlcat_1()` appends `"test"` into an empty 32-byte destination and expects destination text plus return value 4. `test_strlcat_2()` passes `strlen(dst)` as size while `dst` is empty, expecting no modification and return value equal to source length.

Control flow/state: stack buffers are reset per test. Pointer/string comparisons use CUnit assertions.

Dependencies/integration: includes fio fallback `../../oslib/strlcat.h` unless `CONFIG_STRLCAT` selects libc.

Risks/test signals: verifies basic append and zero-size semantics. Missing coverage includes truncation with non-empty destination, return value under truncation, exact-fit buffers, and unterminated destination edge cases.
