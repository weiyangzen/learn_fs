<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/creat/creat07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/creat/creat07.c

Purpose: LTP regression coverage for `creat` behavior. Source intent: Copyright (c) International Business Machines Corp., 2001 Copyright (c) 2012-2016 Cyril Hrubis <chrubis@suse.cz> \ Check that :manpage:`creat(2)` sets ETXTBSY correctly. The file was read in full for this report (69 lines, 1338 bytes).

Important APIs/types/functions: Primary functions are `verify_creat`, `setup`. Important call/API signals are `creat`, `verify_creat`, `SAFE_FORK`, `SAFE_EXECL`, `TST_CHECKPOINT_WAIT`, `TEST`, `tst_res`, `SAFE_KILL`, `SAFE_WAITPID`, `tst_kvercmp`, `tst_brk`. Defined constants/macros include `TEST_APP`. Harness metadata uses `.test_all`, `.setup`, `.needs_checkpoints`, `.resource_files`, `.forks_child`.

Control flow: The test is organized around setup-oriented functions `setup`; verify-oriented functions `verify_creat`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, child processes and exit status. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<sys/types.h>`, `<sys/stat.h>`, `<sys/wait.h>`, `<stdio.h>`, `<stdlib.h>`, `<errno.h>`, `<fcntl.h>`, `"tst_test.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `creat` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: permission, umask, setgid, and resource-limit behavior depends on credentials and filesystem mode bits

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `ETXTBSY, EXTBSY, O_WRONLY`; harness fields `.test_all, .setup, .needs_checkpoints, .resource_files, .forks_child`; TCONF skip paths for unsupported kernel, libc, privilege, device, or filesystem conditions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/creat/creat07.c -->
