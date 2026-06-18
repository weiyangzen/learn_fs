<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/dup/dup03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/dup/dup03.c

Purpose: LTP regression coverage for `dup` behavior. Source intent: Copyright (c) 2000 Silicon Graphics, Inc. Copyright (c) 2020 SUSE LLC \ Verify that dup(2) syscall fails with errno EMFILE when the per-process limit on the number of open file descriptors has been reached. The file was read in full for this report (56 lines, 995 bytes).

Important APIs/types/functions: Primary functions are `run`, `setup`, `cleanup`. Important call/API signals are `TST_EXP_FAIL2`, `SAFE_CLOSE`, `SAFE_SYSCONF`, `SAFE_MALLOC`, `SAFE_OPEN`, `SAFE_DUP`. Harness metadata uses `.test_all`, `.setup`, `.cleanup`, `.needs_tmpdir`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdlib.h>`, `"tst_test.h"`; the modern LTP `struct tst_test` harness; an isolated LTP temporary directory. It integrates with the sibling `dup` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: expected errno and return-value assertions are sensitive to kernel, libc, and architecture ABI differences

Test signals: explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EMFILE, O_RDWR, O_CREAT`; harness fields `.test_all, .setup, .cleanup, .needs_tmpdir`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/dup/dup03.c -->
