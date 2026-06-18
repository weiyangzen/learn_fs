<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/dup/dup04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/dup/dup04.c

Purpose: LTP regression coverage for `dup` behavior. Source intent: Copyright (c) 2000 Silicon Graphics, Inc. 06/1994 AUTHOR: Richard Logan CO-PILOT: William Roske Copyright (c) 2023 SUSE LLC \ Basic test for dup(2) of a system pipe descriptor. The file was read in full for this report (41 lines, 707 bytes).

Important APIs/types/functions: Primary functions are `run`, `setup`. Important call/API signals are `TST_EXP_FD`, `SAFE_CLOSE`, `SAFE_PIPE`. Defined constants/macros include `_GNU_SOURCE`. Harness metadata uses `.test_all`, `.setup`, `.needs_tmpdir`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, pollable descriptor readiness state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `"tst_test.h"`; the modern LTP `struct tst_test` harness; an isolated LTP temporary directory. It integrates with the sibling `dup` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: expected errno and return-value assertions are sensitive to kernel, libc, and architecture ABI differences

Test signals: harness fields `.test_all, .setup, .needs_tmpdir`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/dup/dup04.c -->
