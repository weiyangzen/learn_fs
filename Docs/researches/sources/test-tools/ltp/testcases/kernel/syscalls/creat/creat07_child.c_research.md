<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/creat/creat07_child.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/creat/creat07_child.c

Purpose: LTP regression coverage for `creat` behavior. Source intent: Copyright (c) International Business Machines Corp., 2001 Copyright (c) 2012 Cyril Hrubis <chrubis@suse.cz> The file was read in full for this report (21 lines, 321 bytes).

Important APIs/types/functions: Primary functions are `main`. Important call/API signals are `tst_reinit`, `TST_CHECKPOINT_WAKE`. Defined constants/macros include `TST_NO_DEFAULT_MAIN`. The file has little or no explicit LTP harness metadata.

Control flow: The test is organized around entry/helper functions `main`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test keeps state local to automatic variables and LTP harness bookkeeping. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<unistd.h>`, `"tst_test.h"`; the modern LTP `struct tst_test` harness; legacy LTP harness APIs. It integrates with the sibling `creat` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: permission, umask, setgid, and resource-limit behavior depends on credentials and filesystem mode bits

Test signals: return values, errno, and LTP result records are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/creat/creat07_child.c -->
