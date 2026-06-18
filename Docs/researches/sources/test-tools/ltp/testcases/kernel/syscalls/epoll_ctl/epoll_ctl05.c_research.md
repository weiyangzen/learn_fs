<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_ctl/epoll_ctl05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/epoll_ctl/epoll_ctl05.c

Purpose: LTP regression coverage for `epoll_ctl` behavior. Source intent: Copyright (c) Linux Test Project, 2021 Author: Xie Ziyao <ziyaoxie@outlook.com> \ Verify that epoll_ctl() fails with ELOOP if fd refers to an epoll instance and this EPOLL_CTL_ADD operation would result in a circular loop of epoll instances monitoring one another. The file was read in full for this report (70 lines, 1508 bytes).

Important APIs/types/functions: Primary functions are `setup`, `cleanup`, `verify_epoll_ctl`. Important call/API signals are `epoll_ctl`, `SAFE_PIPE`, `epoll_create`, `tst_brk`, `SAFE_CLOSE`, `verify_epoll_ctl`, `TST_EXP_FAIL`. Defined constants/macros include `MAX_DEPTH`. Relevant structs/types include `struct epoll_event`. Harness metadata uses `.test_all`, `.setup`, `.cleanup`.

Control flow: The test is organized around setup-oriented functions `setup`; verify-oriented functions `verify_epoll_ctl`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, pollable descriptor readiness state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<poll.h>`, `<sys/epoll.h>`, `"tst_test.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `epoll_ctl` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: readiness results depend on descriptor lifetime, nonblocking mode, and timing

Test signals: explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `ELOOP, EPOLLIN, EPOLL_CTL_ADD, EPOLL_CTL_DEL`; harness fields `.test_all, .setup, .cleanup`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_ctl/epoll_ctl05.c -->
