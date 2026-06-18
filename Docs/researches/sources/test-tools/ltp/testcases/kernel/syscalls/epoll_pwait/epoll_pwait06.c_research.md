<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_pwait/epoll_pwait06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/epoll_pwait/epoll_pwait06.c

Purpose: LTP regression coverage for `epoll_pwait` behavior. Source intent: Copyright (c) 2025 SUSE LLC <mdoucha@suse.cz> \ Verify that various timeout values don't get misinterpreted as infinity by epoll_pwait() and epoll_pwait2(). Regression fixed in: commit d9ec73301099ec5975505e1c3effbe768bab9490 Author: Max Kellermann <max.kellermann@ionos.com> Date: Tue Apr 29 20:58:27 2025 +0200 fs/eventpoll: fix endless busy loop after timeout has expired File descriptor types not supported by epoll The file was read in full for this report (89 lines, 1803 bytes).

Important APIs/types/functions: Primary functions are `run`, `setup`, `cleanup`. Important call/API signals are `epoll_pwait`, `epoll_pwait2`, `TST_FD_FOREACH`, `tst_res`, `tst_fd_desc`, `SAFE_EPOLL_CTL`, `do_epoll_pwait`, `epoll_pwait_init`, `SAFE_EPOLL_CREATE1`, `SAFE_CLOSE`. Relevant structs/types include `struct timespec`, `struct epoll_event`, `struct tst_tag`. Harness metadata uses `.test_all`, `.setup`, `.cleanup`, `.tags`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, kernel clock state or time namespace state, pollable descriptor readiness state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `"tst_test.h"`, `"tst_timer.h"`, `"tst_epoll.h"`, `"epoll_pwait_var.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `epoll_pwait` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: readiness results depend on descriptor lifetime, nonblocking mode, and timing

Test signals: explicit TPASS/TST_EXP_PASS success paths; case/errno constants `EPOLLIN, EPOLL_CTL_ADD, EPOLL_CTL_DEL`; harness fields `.test_all, .setup, .cleanup, .tags`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_pwait/epoll_pwait06.c -->
