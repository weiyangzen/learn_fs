<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_ctl/epoll_ctl02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/epoll_ctl/epoll_ctl02.c

Purpose: LTP regression coverage for `epoll_ctl` behavior. Source intent: Copyright (c) 2016 Fujitsu Ltd. Author: Xiao Yang <yangx.jy@cn.fujitsu.com> \ Verify that epoll_ctl() fails with: - EBADF if epfd is an invalid fd. - EPERM if fd does not support epoll. - ENOENT if fd is not registered with EPOLL_CTL_DEL. - ENOENT if fd is not registered with EPOLL_CTL_MOD. The file was read in full for this report (95 lines, 2499 bytes).

Important APIs/types/functions: Primary functions are `setup`, `cleanup`, `verify_epoll_ctl`. Important call/API signals are `epoll_ctl`, `SAFE_OPEN`, `epoll_create`, `tst_brk`, `SAFE_PIPE`, `SAFE_CLOSE`, `verify_epoll_ctl`, `TST_EXP_FAIL`. Relevant structs/types include `struct epoll_event`, `struct testcase`. Harness metadata uses `.test`, `.setup`, `.cleanup`, `.tcnt`.

Control flow: The test is organized around setup-oriented functions `setup`; verify-oriented functions `verify_epoll_ctl`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, pollable descriptor readiness state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<poll.h>`, `<sys/epoll.h>`, `"tst_test.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `epoll_ctl` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: readiness results depend on descriptor lifetime, nonblocking mode, and timing

Test signals: explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EBADF, EPERM, EINVAL, ENOENT, EEXIST, EPOLLIN, EPOLLOUT, EFAULT, EPOLL_CTL_DEL, EPOLL_CTL_MOD, EPOLL_CTL_ADD, O_RDONLY, O_DIRECTORY`; harness fields `.test, .setup, .cleanup, .tcnt`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_ctl/epoll_ctl02.c -->
