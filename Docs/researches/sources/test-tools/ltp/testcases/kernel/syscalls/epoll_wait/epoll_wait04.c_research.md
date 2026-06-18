<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_wait/epoll_wait04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/epoll_wait/epoll_wait04.c

Purpose: LTP regression coverage for `epoll_wait` behavior. Source intent: Copyright (c) Huawei Technologies Co., Ltd. Author: Xie Ziyao <xieziyao@huawei.com> \ Check that a timeout equal to zero causes epoll_wait() to return immediately. The file was read in full for this report (70 lines, 1460 bytes).

Important APIs/types/functions: Primary functions are `run`, `setup`, `cleanup`. Important call/API signals are `epoll_wait`, `tst_timer_start`, `TEST`, `tst_timer_stop`, `tst_res`, `tst_timer_elapsed_us`, `SAFE_PIPE`, `epoll_create`, `tst_brk`, `epoll_ctl`, `SAFE_CLOSE`. Defined constants/macros include `USEC_PRECISION`. Relevant structs/types include `struct epoll_event`. Harness metadata uses `.test_all`, `.setup`, `.cleanup`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, kernel clock state or time namespace state, pollable descriptor readiness state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<sys/epoll.h>`, `"tst_test.h"`, `"tst_timer_test.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `epoll_wait` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: readiness results depend on descriptor lifetime, nonblocking mode, and timing

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EPOLLIN, CLOCK_MONOTONIC, EPOLL_CTL_ADD`; harness fields `.test_all, .setup, .cleanup`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_wait/epoll_wait04.c -->
