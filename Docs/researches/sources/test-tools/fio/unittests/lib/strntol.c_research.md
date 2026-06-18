# sources/test-tools/fio/unittests/lib/strntol.c

Purpose: CUnit tests for bounded string-to-long parsing.

Important APIs/functions: `test_strntol_1()` parses a simple decimal string. `test_strntol_2()` checks leading whitespace. `test_strntol_3()` parses a hexadecimal string with explicit base 16. Each verifies the numeric result, non-NULL end pointer, and end-of-string termination. `fio_unittest_lib_strntol()` registers the suite.

Control flow/state: each test uses a local mutable string and passes its exact `strlen()` length to `strntol()`.

Dependencies/integration: depends on `../../lib/strntol.h` and CUnit. It validates compatibility with libc-style `strtol` behavior while respecting a maximum length.

Risks/test signals: good basic parser coverage, but missing invalid input, overflow/underflow, truncated length, sign handling, base auto-detection, and end-pointer positioning before the provided length.
