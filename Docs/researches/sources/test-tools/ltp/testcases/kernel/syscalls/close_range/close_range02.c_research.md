<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/close_range/close_range02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/close_range/close_range02.c

Purpose: LTP regression coverage for `close_range` behavior. Source intent: Copyright (c) 2021 SUSE LLC \ - First check close_range works on a valid range. - Then check close_range does not accept invalid paramters. - Then check it accepts a large lower fd. - Finally check CLOEXEC works The file was read in full for this report (114 lines, 2355 bytes).

Important APIs/types/functions: Primary functions are `try_close_range`, `run`. Important call/API signals are `try_close_range`, `TEST`, `close_range`, `SAFE_OPEN`, `SAFE_DUP2`, `TST_EXP_PASS`, `TST_EXP_FAIL`, `fcntl`, `tst_res`, `TST_EXP_FD_SILENT`, `SAFE_CLONE`, `tst_reap_children`, `TST_EXP_PASS_SILENT`. Relevant structs/types include `struct tst_clone_args`. Harness metadata uses `.test`, `.setup`, `.tcnt`, `.forks_child`.

Control flow: The test is organized around run-oriented functions `run`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, local sockets and network namespace state, child processes and exit status. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdlib.h>`, `"tst_test.h"`, `"tst_clone.h"`, `"lapi/fcntl.h"`, `"lapi/close_range.h"`, `"lapi/sched.h"`; the modern LTP `struct tst_test` harness; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps. It integrates with the sibling `close_range` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: descriptor ranges can accidentally close harness fds if setup bounds are wrong

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EINVAL, EBADF, CLONE_FILES, O_PATH, F_GETFD, CLOSE_RANGE_CLOEXEC, FD_CLOEXEC, CLOSE_RANGE_UNSHARE`; harness fields `.test, .setup, .tcnt, .forks_child`; TCONF skip paths for unsupported kernel, libc, privilege, device, or filesystem conditions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/close_range/close_range02.c -->
