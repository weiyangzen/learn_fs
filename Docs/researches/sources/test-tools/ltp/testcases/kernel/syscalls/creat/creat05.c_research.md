<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/creat/creat05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/creat/creat05.c

Purpose: LTP regression coverage for `creat` behavior. Source intent: Copyright (c) International Business Machines Corp., 2001 Ported to LTP: Wayne Boyer \ Check that :manpage:`creat(2)` system call returns EMFILE. The file was read in full for this report (83 lines, 1688 bytes).

Important APIs/types/functions: Primary functions are `verify_creat`, `setup`, `cleanup`. Important call/API signals are `creat`, `verify_creat`, `TEST`, `tst_res`, `SAFE_CLOSE`, `SAFE_MALLOC`, `SAFE_CREAT`, `close`. Harness metadata uses `.test_all`, `.setup`, `.cleanup`, `.needs_tmpdir`.

Control flow: The test is organized around setup-oriented functions `setup`; verify-oriented functions `verify_creat`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdio.h>`, `<stdlib.h>`, `<errno.h>`, `<sys/types.h>`, `<sys/time.h>`, `<sys/resource.h>`, `<sys/stat.h>`, `<fcntl.h>`, `<linux/limits.h>`, `<unistd.h>`; the modern LTP `struct tst_test` harness; an isolated LTP temporary directory. It integrates with the sibling `creat` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: permission, umask, setgid, and resource-limit behavior depends on credentials and filesystem mode bits

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EMFILE`; harness fields `.test_all, .setup, .cleanup, .needs_tmpdir`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/creat/creat05.c -->
