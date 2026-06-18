# sources/test-tools/unionmount-testsuite/tests/rename-mass.py

Purpose: the simplest mass-rename file test, rotating an existing sequence of lower regular files through a fixed ring and then deleting the survivors.

Important APIs and functions: defines `subtest_1(ctx)` for circular `ctx.rename()` calls and `subtest_2(ctx)` for cleanup with `ctx.unlink()`. It imports `errno` for `ENOENT`.

Control flow: `subtest_1` starts with the gap at the last ring index and repeatedly moves the previous entry into the gap. `subtest_2` calculates the final gap and expects it to be absent.

State and persistence: the namespace state is the only persistent state. Data content is not read; the test is focused on dentry existence and rename success.

Dependencies and integration: depends on `ctx.reg_file()` generating a numeric base compatible with suffixes `100..106`. It is invoked by the harness as numbered subtests.

Risks: because no file content is checked, rename implementations that preserve existence but swap payloads incorrectly may escape this test.

Test signals: all rename calls succeed and exactly one `unlink` reports `ENOENT` during cleanup.
