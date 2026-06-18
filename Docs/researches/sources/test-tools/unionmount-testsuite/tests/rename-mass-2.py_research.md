# sources/test-tools/unionmount-testsuite/tests/rename-mass-2.py

Purpose: stress test for repeated mass renames of a small range of lower regular files through sequential suffix generations.

Important APIs/types/functions: constants `file_count = 104`, `iter_count = 3`, `subtest_1`, and `subtest_2`.

Control flow: `subtest_1` derives the base `foo` path, renames files `foo100` through `foo103` to `_0`, then for three iterations renames each file in reverse order from suffix `_j` to `_j+1`. `subtest_2` unlinks the final `_3` names.

State and persistence: repeatedly moves lower-file names into upper/whiteout state and then deletes them. Context tracks each rename/unlink.

Dependencies and integration: uses `ctx.rename` and `ctx.unlink` with setup regular files.

Risks: small file range limits stress; reverse iteration avoids name collisions but still exercises dense rename metadata updates.

Test signals: catches rename scalability/state leaks across repeated file moves.
