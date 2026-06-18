# sources/test-tools/ltp/testcases/kernel/syscalls/eventfd/eventfd02.c

Purpose: Checks core `eventfd()` write semantics and error handling on a nonblocking descriptor.

Important APIs/types/functions: `eventfd(0, EFD_NONBLOCK)`, `SAFE_WRITE`, `SAFE_READ`, raw `write()`, `TST_EXP_FD`, `TST_EXP_FAIL`, `TST_EXP_EQ_LI`, and the `CONFIG_EVENTFD` kconfig requirement.

Control flow: The test creates an eventfd, writes value 12, reads it back, fills the counter to `UINT64_MAX - 1`, verifies a further write returns `EAGAIN`, verifies short writes return `EINVAL`, then verifies writing `UINT64_MAX` is rejected.

State and persistence behavior: The only kernel state is the in-kernel eventfd counter and descriptor flags. The counter is explicitly drained once and then saturated to exercise boundary behavior.

Dependencies and integration points: Runs through the LTP `struct tst_test` `.test_all` path and requires `CONFIG_EVENTFD`; no tmpdir or fork support is needed.

Risks and test signals: Boundary arithmetic is the risk: if counter saturation or buffer-size validation regresses, the fail/pass macros expose wrong errno or value. The source comment mentions zero/nonblocking behavior, but this implementation primarily validates write saturation and invalid write formats.
