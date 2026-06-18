# sources/test-tools/fio/unittests/lib/memalign.c

Purpose: CUnit smoke test for fio's internal aligned allocation helper.

Important APIs/functions: `test_memalign_1()` calls `__fio_memalign(4096, 1234, malloc)` and, if allocation succeeds, asserts the returned pointer is aligned to 4096 bytes. `fio_unittest_lib_memalign()` registers the suite as `lib/memalign.c`.

Control flow/state: one allocation is performed and checked. The test does not free the returned pointer in this file, so its scope is a short-lived unit-test process.

Dependencies/integration: includes `../../lib/memalign.h`, CUnit wrappers from `../unittest.h`, and libc `malloc`.

Risks/test signals: pointer alignment is checked by casting to `int`, which can truncate on 64-bit platforms; using `uintptr_t` without narrowing would be safer. It does not assert non-NULL, so allocation failure silently passes. Additional tests should cover multiple alignments, invalid alignments, and freeing.
