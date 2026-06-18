<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/dup/dup02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/dup/dup02.c

Purpose: LTP regression coverage for `dup` behavior. Source intent: Copyright (c) 2000 Silicon Graphics, Inc. Copyright (c) 2020 SUSE LLC 03/30/1992 AUTHOR: Richard Logan CO-PILOT: William Roske \ Verify that dup(2) syscall fails with errno EBADF when called with invalid value for oldfd argument. The file was read in full for this report (37 lines, 693 bytes).

Important APIs/types/functions: Primary functions are `run`. Important call/API signals are `TST_EXP_FAIL2`, `SAFE_CLOSE`. Relevant structs/types include `struct tcase`. Harness metadata uses `.test`, `.tcnt`.

Control flow: The test is organized around run-oriented functions `run`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `"tst_test.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `dup` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: expected errno and return-value assertions are sensitive to kernel, libc, and architecture ABI differences

Test signals: explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EBADF`; harness fields `.test, .tcnt`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/dup/dup02.c -->
