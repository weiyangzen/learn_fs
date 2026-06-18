<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/creat/creat09.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/creat/creat09.c

Purpose: LTP regression coverage for `creat` behavior. Source intent: Copyright (c) 2021 SUSE LLC <mdoucha@suse.cz> \ CVE-2018-13405 Check for possible privilege escalation through creating files with setgid bit set inside a setgid directory owned by a group which the user does not belong to. The file was read in full for this report (145 lines, 3200 bytes).

Important APIs/types/functions: Primary functions are `setup`, `file_test`, `run`, `cleanup`. Important call/API signals are `SAFE_GETPWNAM`, `tst_res`, `tst_get_free_gid`, `SAFE_MKDIR`, `SAFE_CHOWN`, `SAFE_CHMOD`, `SAFE_STAT`, `tst_brk`, `SAFE_SETGID`, `SAFE_SETREUID`, `SAFE_CREAT`, `SAFE_CLOSE`, `SAFE_OPEN`, `tst_purge_dir`. Defined constants/macros include `MODE_RWX`, `MODE_SGID`, `MNTPOINT`, `WORKDIR`, `CREAT_FILE`, `OPEN_FILE`. Relevant structs/types include `struct tcase`, `struct stat`, `struct passwd`, `struct tst_tag`. Harness metadata uses `.test`, `.setup`, `.cleanup`, `.tcnt`, `.needs_root`, `.tags`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run`; test-oriented functions `file_test`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, effective UID/GID or Linux capability state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdlib.h>`, `<sys/types.h>`, `<pwd.h>`, `"tst_test.h"`, `"tst_uid.h"`; the modern LTP `struct tst_test` harness; root privileges or selected Linux capabilities. It integrates with the sibling `creat` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: permission, umask, setgid, and resource-limit behavior depends on credentials and filesystem mode bits

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `O_CREAT, O_EXCL, O_RDWR`; harness fields `.test, .setup, .cleanup, .tcnt, .needs_root, .tags`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/creat/creat09.c -->
