<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone05.c

Purpose: LTP regression coverage for `clone` behavior. Source intent: Copyright (c) Wipro Technologies Ltd, 2002. Copyright (c) 2012 Wanlong Gao <gaowanlong@cn.fujitsu.com> Copyright (c) 2012 Cyril Hrubis <chrubis@suse.cz> \ Call clone() with CLONE_VFORK flag set. verify that execution of parent is suspended until child finishes The file was read in full for this report (56 lines, 1095 bytes).

Important APIs/types/functions: Primary functions are `child_fn`, `verify_clone`. Important call/API signals are `clone`, `verify_clone`, `TST_EXP_PID_SILENT`, `ltp_clone`, `TST_EXP_VAL`. Defined constants/macros include `_GNU_SOURCE`. Relevant structs/types include `struct tst_buffers`. Harness metadata uses `.test_all`.

Control flow: The test is organized around verify-oriented functions `verify_clone`; child-oriented functions `child_fn`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates child processes and exit status. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdlib.h>`, `<sched.h>`, `"tst_test.h"`, `"clone_platform.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `clone` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: clone flag semantics are architecture- and kernel-version-sensitive

Test signals: case/errno constants `CLONE_VFORK, CLONE_VM`; harness fields `.test_all`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone05.c -->
