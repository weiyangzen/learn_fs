<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone02.c

Purpose: LTP regression coverage for `clone` behavior. Source intent: Copyright (c) Wipro Technologies Ltd, 2002. Copyright (c) 2012 Wanlong Gao <gaowanlong@cn.fujitsu.com> This program is free software; you can redistribute it and/or modify it under the terms of version 2 of the GNU General Public License as published by the Free Software Foundation. The file was read in full for this report (465 lines, 10536 bytes).

Important APIs/types/functions: Primary functions are `setup`, `test_setup`, `cleanup`, `test_cleanup`, `child_fn`, `parent_test1`, `parent_test2`, `test_VM`, `test_FS`, `test_FILES`, `test_SIG`, `modified_VM`, `modified_FS`, `modified_FILES`, `modified_SIG`, `sig_child_defined_handler`, `sig_default_handler`, `main`. Important call/API signals are `clone`, `tst_parse_opts`, `tst_brkm`, `TEST_LOOPING`, `tst_resm`, `TEST`, `ltp_clone`, `wait`, `WEXITSTATUS`, `tst_exit`, `tst_sig`, `tst_tmpdir`, `syscall`, `tst_rmdir`, `open`, `SAFE_CHDIR`, `close`, `tst_get_tmpdir`, `read`. Defined constants/macros include `_GNU_SOURCE`, `FLAG_ALL`, `FLAG_NONE`, `PARENT_VALUE`, `CHILD_VALUE`, `TRUE`, `FALSE`. Relevant structs/types include `struct test_case_t`, `struct sigaction`. The file has little or no explicit LTP harness metadata.

Control flow: The test is organized around setup-oriented functions `setup, test_setup`; test-oriented functions `test_setup, test_cleanup, parent_test1, parent_test2, test_VM, test_FS`; cleanup-oriented functions `cleanup, test_cleanup`; child-oriented functions `child_fn, sig_child_defined_handler`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, child processes and exit status. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<errno.h>`, `<fcntl.h>`, `<sys/wait.h>`, `<sys/types.h>`, `<sys/syscall.h>`, `<sched.h>`, `"test.h"`, `"tso_safe_macros.h"`, `"tst_clone.h"`, `"clone_platform.h"`; legacy LTP harness APIs. It integrates with the sibling `clone` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: clone flag semantics are architecture- and kernel-version-sensitive

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EBADF, CLONE_VM, CLONE_FS, CLONE_FILES, CLONE_SIGHAND, O_CREAT, O_RDWR`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone02.c -->
