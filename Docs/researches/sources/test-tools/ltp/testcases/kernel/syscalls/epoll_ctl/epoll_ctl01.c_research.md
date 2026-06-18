<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_ctl/epoll_ctl01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/epoll_ctl/epoll_ctl01.c

Purpose: LTP regression coverage for `epoll_ctl` behavior. Source intent: Copyright (c) 2016 Fujitsu Ltd. Author: Xiao Yang <yangx.jy@cn.fujitsu.com> \ Check the basic functionality of the epoll_ctl: - When epoll_ctl succeeds to register fd on the epoll instance and associates event with fd, epoll_wait will get registered fd and event correctly. - When epoll_ctl succeeds to change event which is related to fd, epoll_wait will get changed event correctly. The file was read in full for this report (145 lines, 3134 bytes).

Important APIs/types/functions: Primary functions are `setup`, `cleanup`, `has_event`, `check_epoll_ctl`, `opera_epoll_ctl`, `verify_epoll_ctl`. Important call/API signals are `epoll_create`, `tst_brk`, `SAFE_PIPE`, `SAFE_CLOSE`, `check_epoll_ctl`, `SAFE_WRITE`, `epoll_wait`, `tst_res`, `epoll_ctl`, `SAFE_READ`, `opera_epoll_ctl`, `TEST`, `verify_epoll_ctl`. Relevant structs/types include `struct epoll_event`. Harness metadata uses `.test_all`, `.setup`, `.cleanup`.

Control flow: The test is organized around setup-oriented functions `setup`; verify-oriented functions `verify_epoll_ctl`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, pollable descriptor readiness state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<poll.h>`, `<sys/epoll.h>`, `"tst_test.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `epoll_ctl` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: readiness results depend on descriptor lifetime, nonblocking mode, and timing

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EPOLLIN, EPOLLOUT, EPOLL_CTL_ADD, EPOLL_CTL_MOD, EPOLL_CTL_DEL`; harness fields `.test_all, .setup, .cleanup`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_ctl/epoll_ctl01.c -->
