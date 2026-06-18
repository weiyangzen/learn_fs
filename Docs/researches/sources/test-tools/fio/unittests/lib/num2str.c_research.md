# sources/test-tools/fio/unittests/lib/num2str.c

Purpose: CUnit tests for numeric-to-string helpers in fio's `lib/num2str.h`.

Important APIs/functions: `test_num2str()` iterates table-driven cases for `num2str()` including `UINT64_MAX`, shortened SI output, and precision/length constraints. `test_bytes2str_simple()` checks fixed binary byte-unit formatting from bytes through EiB and asserts the returned pointer equals the caller buffer. `fio_unittest_lib_num2str()` registers both tests.

Control flow/state: table arrays define inputs and expected strings. Each `num2str()` result is freed after assertion; `bytes2str_simple()` uses a stack buffer.

Dependencies/integration: depends on fio compiler array-size macro, `num2str()` allocation semantics, `bytes2str_simple()` buffer semantics, and CUnit.

Risks/test signals: tests cover important boundary values but not every base/unit/power-of-two combination. They also assume exact decimal text, so formatting changes are caught. Missing cases include small buffer behavior and invalid units.
