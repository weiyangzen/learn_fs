<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/close_range/close_range01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/close_range/close_range01.c

Purpose: LTP regression coverage for `close_range` behavior. Source intent: Taken from the kernel self tests, which in turn were based on a Syzkaller reproducer. Self test author and close_range author: Christian Brauner <christian.brauner@ubuntu.com> LTP Author: Richard Palethorpe <rpalethorpe@suse.com> Copyright (c) 2021 SUSE LLC, other copyrights may apply. The file was read in full for this report (211 lines, 4261 bytes).

Important APIs/types/functions: Primary functions are `do_close_range`, `setup`, `check_cloexec`, `check_closed`, `child`, `run`. Important call/API signals are `close_range`, `do_close_range`, `tst_brk`, `close_range_supported_by_kernel`, `SAFE_GETRLIMIT`, `SAFE_SETRLIMIT`, `SAFE_FCNTL`, `tst_res`, `check_closed`, `fcntl`, `SAFE_DUP2`, `SAFE_OPEN`, `SAFE_CLONE`, `tst_reap_children`, `tst_taint_check`, `TST_CAP`. Relevant structs/types include `struct rlimit`, `struct tst_clone_args`, `struct tst_cap`, `struct tst_tag`. Harness metadata uses `.test`, `.setup`, `.tcnt`, `.needs_root`, `.tags`, `.forks_child`, `.taint_check`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run`; child-oriented functions `child`; do_-oriented functions `do_close_range`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, child processes and exit status, effective UID/GID or Linux capability state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdlib.h>`, `"tst_test.h"`, `"tst_clone.h"`, `"lapi/sched.h"`, `"lapi/close_range.h"`; the modern LTP `struct tst_test` harness; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps; root privileges or selected Linux capabilities. It integrates with the sibling `close_range` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: descriptor ranges can accidentally close harness fds if setup bounds are wrong

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EINVAL, CLOSE_RANGE_UNSHARE, CLOSE_RANGE_CLOEXEC, F_GETFD, FD_CLOEXEC, CLONE_FILES, O_RDWR, O_CREAT`; harness fields `.test, .setup, .tcnt, .needs_root, .tags, .forks_child, .taint_check`; TCONF skip paths for unsupported kernel, libc, privilege, device, or filesystem conditions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/close_range/close_range01.c -->
