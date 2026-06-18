<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/dup/dup06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/dup/dup06.c

Purpose: LTP regression coverage for `dup` behavior. Source intent: Copyright (c) International Business Machines Corp., 2002 Ported from SPIE, section2/iosuite/dup1.c, by Airong Zhang Copyright (c) 2013 Cyril Hrubis <chrubis@suse.cz> Copyright (c) Linux Test Project, 2003-2024 \ Test for dup(2) syscall with max open file descriptors. The file was read in full for this report (78 lines, 1589 bytes).

Important APIs/types/functions: Primary functions are `cnt_free_fds`, `setup`, `cleanup`, `run`. Important call/API signals are `fcntl`, `SAFE_MALLOC`, `SAFE_CREAT`, `tst_res`, `SAFE_UNLINK`, `SAFE_CLOSE`. Harness metadata uses `.test_all`, `.setup`, `.cleanup`, `.needs_tmpdir`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdlib.h>`, `"tst_test.h"`; the modern LTP `struct tst_test` harness; an isolated LTP temporary directory. It integrates with the sibling `dup` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: expected errno and return-value assertions are sensitive to kernel, libc, and architecture ABI differences

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EBADF, F_GETFD`; harness fields `.test_all, .setup, .cleanup, .needs_tmpdir`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/dup/dup06.c -->
