<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone03.c

Purpose: LTP regression coverage for `clone` behavior. Source intent: Copyright (c) Wipro Technologies Ltd, 2002. Copyright (c) 2012 Wanlong Gao <gaowanlong@cn.fujitsu.com> \ Check for equality of getpid() from a child and return value of clone(2) The file was read in full for this report (60 lines, 1158 bytes).

Important APIs/types/functions: Primary functions are `child_fn`, `verify_clone`, `setup`, `cleanup`. Important call/API signals are `clone`, `verify_clone`, `TST_EXP_PID_SILENT`, `ltp_clone`, `tst_reap_children`, `TST_EXP_VAL`, `SAFE_MMAP`, `SAFE_MUNMAP`. Relevant structs/types include `struct tst_buffers`. Harness metadata uses `.test_all`, `.setup`, `.cleanup`.

Control flow: The test is organized around setup-oriented functions `setup`; verify-oriented functions `verify_clone`; cleanup-oriented functions `cleanup`; child-oriented functions `child_fn`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates child processes and exit status. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdio.h>`, `<stdlib.h>`, `"tst_test.h"`, `"clone_platform.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `clone` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: clone flag semantics are architecture- and kernel-version-sensitive

Test signals: harness fields `.test_all, .setup, .cleanup`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone03.c -->
