<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_ctl/epoll_ctl03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/epoll_ctl/epoll_ctl03.c

Purpose: LTP regression coverage for `epoll_ctl` behavior. Source intent: Copyright (c) Linux Test Project, 2021 Author: Xie Ziyao <ziyaoxie@outlook.com> \ Check that epoll_ctl returns zero with different combinations of events on success. The file was read in full for this report (76 lines, 1567 bytes).

Important APIs/types/functions: Primary functions are `run_all`, `setup`, `cleanup`. Important call/API signals are `TST_IS_BIT_SET`, `TST_EXP_PASS`, `epoll_ctl`, `epoll_create`, `tst_brk`, `SAFE_PIPE`, `SAFE_CLOSE`. Defined constants/macros include `NUM_EPOLL_EVENTS`, `WIDTH_EPOLL_EVENTS`. Relevant structs/types include `struct epoll_event`. Harness metadata uses `.test_all`, `.setup`, `.cleanup`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run_all`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, pollable descriptor readiness state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<poll.h>`, `<sys/epoll.h>`, `"tst_test.h"`, `"tst_bitmap.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `epoll_ctl` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: readiness results depend on descriptor lifetime, nonblocking mode, and timing

Test signals: explicit TPASS/TST_EXP_PASS success paths; case/errno constants `EPOLLIN, EPOLLOUT, EPOLLPRI, EPOLLERR, EPOLLHUP, EPOLLET, EPOLLONESHOT, EPOLLRDHUP, EPOLL_CTL_MOD, EPOLL_CTL_ADD`; harness fields `.test_all, .setup, .cleanup`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_ctl/epoll_ctl03.c -->
