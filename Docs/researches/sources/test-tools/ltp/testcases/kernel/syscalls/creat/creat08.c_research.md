<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/creat/creat08.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/creat/creat08.c

Purpose: LTP regression coverage for `creat` behavior. Source intent: Copyright (c) International Business Machines Corp., 2002 Ported from SPIE by Airong Zhang <zhanga@us.ibm.com> Copyright (c) 2021 SUSE LLC <mdoucha@suse.cz> \ Verify that the group ID and setgid bit are set correctly when a new file is created with :manpage:`creat(2)`. Create directories and set permissions Switch to user nobody and create two files in DIR_A Both files should inherit GID from the process Create two. The file was read in full for this report (140 lines, 3501 bytes).

Important APIs/types/functions: Primary functions are `setup`, `file_test`, `run`, `cleanup`. Important call/API signals are `creat`, `SAFE_GETPWNAM`, `tst_res`, `tst_get_free_gid`, `SAFE_CREAT`, `SAFE_STAT`, `SAFE_CLOSE`, `SAFE_MKDIR`, `SAFE_CHOWN`, `tst_brk`, `SAFE_CHMOD`, `SAFE_SETGID`, `SAFE_SETREUID`, `tst_purge_dir`, `tst_tmpdir_path`. Defined constants/macros include `MODE_RWX`, `MODE_SGID`, `DIR_A`, `DIR_B`, `SETGID_A`, `NOSETGID_A`, `SETGID_B`, `NOSETGID_B`, `ROOT_SETGID`. Relevant structs/types include `struct passwd`, `struct stat`. Harness metadata uses `.test_all`, `.setup`, `.cleanup`, `.needs_root`, `.needs_tmpdir`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run`; test-oriented functions `file_test`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, effective UID/GID or Linux capability state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdlib.h>`, `<sys/types.h>`, `<pwd.h>`, `"tst_test.h"`, `"tst_uid.h"`; the modern LTP `struct tst_test` harness; root privileges or selected Linux capabilities; an isolated LTP temporary directory. It integrates with the sibling `creat` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: permission, umask, setgid, and resource-limit behavior depends on credentials and filesystem mode bits

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; harness fields `.test_all, .setup, .cleanup, .needs_root, .needs_tmpdir`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/creat/creat08.c -->
