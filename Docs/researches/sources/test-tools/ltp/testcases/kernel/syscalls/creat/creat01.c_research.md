<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/creat/creat01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/creat/creat01.c

Purpose: LTP regression coverage for `creat` behavior. Source intent: Copyright (c) International Business Machines Corp., 2001 Ported to LTP: Wayne Boyer \ 1. The file was read in full for this report (77 lines, 1467 bytes).

Important APIs/types/functions: Primary functions are `setup`, `verify_creat`, `cleanup`. Important call/API signals are `creat`, `verify_creat`, `SAFE_CREAT`, `SAFE_STAT`, `tst_res`, `write`, `read`, `SAFE_CLOSE`. Relevant structs/types include `struct tcase`, `struct stat`. Harness metadata uses `.test`, `.setup`, `.cleanup`, `.tcnt`, `.needs_tmpdir`.

Control flow: The test is organized around setup-oriented functions `setup`; verify-oriented functions `verify_creat`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<sys/types.h>`, `<sys/stat.h>`, `<fcntl.h>`, `<stdio.h>`, `"tst_test.h"`; the modern LTP `struct tst_test` harness; an isolated LTP temporary directory. It integrates with the sibling `creat` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: permission, umask, setgid, and resource-limit behavior depends on credentials and filesystem mode bits

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; harness fields `.test, .setup, .cleanup, .tcnt, .needs_tmpdir`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/creat/creat01.c -->
