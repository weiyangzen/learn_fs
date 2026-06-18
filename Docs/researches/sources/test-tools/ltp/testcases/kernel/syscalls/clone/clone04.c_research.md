<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone04.c

Purpose: LTP regression coverage for `clone` behavior. Source intent: Copyright (c) Wipro Technologies Ltd, 2002. Copyright (c) 2012 Wanlong Gao <gaowanlong@cn.fujitsu.com> Copyright (c) Linux Test Project, 2003-2023 \ Verify that clone(2) fails with - EINVAL if child stack is set to NULL The file was read in full for this report (51 lines, 1047 bytes).

Important APIs/types/functions: Primary functions are `child_fn`, `verify_clone`. Important call/API signals are `clone`, `verify_clone`, `TST_EXP_FAIL`, `ltp_clone`. Relevant structs/types include `struct tcase`, `struct tst_tag`. Harness metadata uses `.test`, `.tcnt`, `.tags`.

Control flow: The test is organized around verify-oriented functions `verify_clone`; child-oriented functions `child_fn`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates child processes and exit status. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdlib.h>`, `"tst_test.h"`, `"clone_platform.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `clone` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: clone flag semantics are architecture- and kernel-version-sensitive

Test signals: explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EINVAL`; harness fields `.test, .tcnt, .tags`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone04.c -->
