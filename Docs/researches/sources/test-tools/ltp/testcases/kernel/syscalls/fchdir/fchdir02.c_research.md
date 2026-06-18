# sources/test-tools/ltp/testcases/kernel/syscalls/fchdir/fchdir02.c

Purpose: negative `fchdir(2)` test for invalid file descriptors.

Important APIs/types/functions: `fchdir`, `TST_EXP_FAIL`, `EBADF`, and `struct tst_test`.

Control flow: `verify_fchdir()` uses a hard-coded invalid descriptor `-5` and asserts that `fchdir` fails with `EBADF`. There is no setup or cleanup because no files are created.

State/persistence behavior: no filesystem or process state should change. The test only observes errno behavior for an invalid fd argument.

Dependencies/integration: minimal modern LTP test with `.test_all`.

Risks/test signals: simple API contract check. Any success or errno other than `EBADF` is reported as failure.
