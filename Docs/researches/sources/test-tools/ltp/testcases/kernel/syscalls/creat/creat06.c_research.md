<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/creat/creat06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/creat/creat06.c

Purpose: LTP regression coverage for `creat` behavior. Source intent: Copyright (c) Linux Test Project, 2014-2026 Copyright (c) International Business Machines Corp., 2001 Ported to LTP: Wayne Boyer \ Check that :manpage:`creat(2)` sets the following errnos correctly: 1. ENAMETOOLONG -- Attempt to :manpage:`creat(2)` a file whose name is more than VFS_MAXNAMLEN and test for ENAMETOOLONG. The file was read in full for this report (140 lines, 3393 bytes).

Important APIs/types/functions: Primary functions are `setup`, `test6_setup`, `test6_cleanup`, `bad_addr_setup`, `verify_creat`. Important call/API signals are `creat`, `verify_creat`, `TEST`, `tst_res`, `tst_strerrno`, `SAFE_GETPWNAM`, `SAFE_MKDIR`, `SAFE_TOUCH`, `SAFE_SYMLINK`, `SAFE_MMAP`, `SAFE_SETEUID`. Defined constants/macros include `TEST_FILE`, `NO_DIR`, `NOT_DIR`, `TEST6_FILE`, `TEST7_FILE`, `TEST8_FILE`, `MODE1`, `MODE2`. Relevant structs/types include `struct passwd`, `struct test_case_t`. Harness metadata uses `.test`, `.setup`, `.tcnt`, `.needs_root`.

Control flow: The test is organized around setup-oriented functions `setup, test6_setup, bad_addr_setup`; verify-oriented functions `verify_creat`; test-oriented functions `test6_setup, test6_cleanup`; cleanup-oriented functions `test6_cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, effective UID/GID or Linux capability state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<errno.h>`, `<string.h>`, `<limits.h>`, `<pwd.h>`, `<sys/mman.h>`, `<sys/types.h>`, `<sys/stat.h>`, `<sys/mount.h>`, `"tst_test.h"`; the modern LTP `struct tst_test` harness; root privileges or selected Linux capabilities. It integrates with the sibling `creat` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: permission, umask, setgid, and resource-limit behavior depends on credentials and filesystem mode bits

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EISDIR, ENAMETOOLONG, ENOENT, ENOTDIR, EFAULT, EACCES, ELOOP, EROFS`; harness fields `.test, .setup, .tcnt, .needs_root`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/creat/creat06.c -->
