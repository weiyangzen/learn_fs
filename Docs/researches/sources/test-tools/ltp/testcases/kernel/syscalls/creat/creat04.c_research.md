<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/creat/creat04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/creat/creat04.c

Purpose: LTP regression coverage for `creat` behavior. Source intent: Copyright (c) International Business Machines Corp., 2001 Ported to LTP: Wayne Boyer \ Check :manpage:`creat(2)` fails with EACCES. The file was read in full for this report (79 lines, 1349 bytes).

Important APIs/types/functions: Primary functions are `child_fn`, `verify_creat`, `setup`. Important call/API signals are `creat`, `SAFE_SETEUID`, `TEST`, `SAFE_UNLINK`, `tst_res`, `verify_creat`, `SAFE_FORK`, `SAFE_GETPWNAM`, `SAFE_MKDIR`, `SAFE_OPEN`, `SAFE_CLOSE`. Defined constants/macros include `DIRNAME`, `FILENAME`. Relevant structs/types include `struct tcase`, `struct passwd`. Harness metadata uses `.test`, `.setup`, `.tcnt`, `.needs_root`, `.needs_tmpdir`, `.forks_child`.

Control flow: The test is organized around setup-oriented functions `setup`; verify-oriented functions `verify_creat`; child-oriented functions `child_fn`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, child processes and exit status, effective UID/GID or Linux capability state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdio.h>`, `<errno.h>`, `<fcntl.h>`, `<pwd.h>`, `<sys/types.h>`, `<sys/stat.h>`, `"tst_test.h"`; the modern LTP `struct tst_test` harness; root privileges or selected Linux capabilities; an isolated LTP temporary directory. It integrates with the sibling `creat` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: permission, umask, setgid, and resource-limit behavior depends on credentials and filesystem mode bits

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EACCES, O_RDWR, O_CREAT`; harness fields `.test, .setup, .tcnt, .needs_root, .needs_tmpdir, .forks_child`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/creat/creat04.c -->
