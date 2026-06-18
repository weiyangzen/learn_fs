<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/close/close02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/close/close02.c

Purpose: LTP regression coverage for `close` behavior. Source intent: Copyright (c) International Business Machines Corp., 2001 07/2001 Ported by Wayne Boyer \ Verify :manpage:`close(2)` failure cases: 1) close(-1) returns EBADF. 2) closing the same fd twice returns EBADF on the second call. The file was read in full for this report (51 lines, 1031 bytes).

Important APIs/types/functions: Primary functions are `verify_close`, `setup`. Important call/API signals are `close`, `verify_close`, `TST_EXP_FAIL`, `SAFE_OPEN`, `tst_brk`. Relevant structs/types include `struct tcase`. Harness metadata uses `.test`, `.setup`, `.tcnt`, `.needs_tmpdir`.

Control flow: The test is organized around setup-oriented functions `setup`; verify-oriented functions `verify_close`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<errno.h>`, `<fcntl.h>`, `"tst_test.h"`; the modern LTP `struct tst_test` harness; an isolated LTP temporary directory. It integrates with the sibling `close` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: expected errno and return-value assertions are sensitive to kernel, libc, and architecture ABI differences

Test signals: explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EBADF, O_CREAT, O_RDWR`; harness fields `.test, .setup, .tcnt, .needs_tmpdir`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/close/close02.c -->
