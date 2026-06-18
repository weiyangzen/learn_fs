<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone07.c

Purpose: LTP regression coverage for `clone` behavior. Source intent: Copyright (c) International Business Machines Corp., 2003. Copyright (c) 2012 Wanlong Gao <gaowanlong@cn.fujitsu.com> \ Test for a libc bug where exiting child function by returning from it caused SIGSEGV. The file was read in full for this report (59 lines, 1228 bytes).

Important APIs/types/functions: Primary functions are `do_child`, `verify_clone`. Important call/API signals are `verify_clone`, `TST_EXP_PID_SILENT`, `ltp_clone`, `SAFE_WAITPID`, `WEXITSTATUS`, `tst_res`, `tst_strstatus`. Relevant structs/types include `struct tst_buffers`. Harness metadata uses `.test_all`.

Control flow: The test is organized around verify-oriented functions `verify_clone`; child-oriented functions `do_child`; do_-oriented functions `do_child`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates child processes and exit status. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<sched.h>`, `<stdio.h>`, `<stdlib.h>`, `"tst_test.h"`, `"lapi/syscalls.h"`, `"clone_platform.h"`; the modern LTP `struct tst_test` harness; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps. It integrates with the sibling `clone` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: clone flag semantics are architecture- and kernel-version-sensitive

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; harness fields `.test_all`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone/clone07.c -->
