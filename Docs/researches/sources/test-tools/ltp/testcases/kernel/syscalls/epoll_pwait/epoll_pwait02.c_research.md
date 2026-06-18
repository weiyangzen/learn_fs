<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_pwait/epoll_pwait02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/epoll_pwait/epoll_pwait02.c

Purpose: LTP regression coverage for `epoll_pwait` behavior. Source intent: Copyright (c) Huawei Technologies Co., Ltd. Author: Xie Ziyao <xieziyao@huawei.com> \ Basic test for epoll_pwait and epoll_pwait2. Checks if data avaiable in a file descriptor are reported correctly in the syscall return value. The file was read in full for this report (65 lines, 1318 bytes).

Important APIs/types/functions: Primary functions are `run`, `setup`, `cleanup`. Important call/API signals are `TEST`, `do_epoll_pwait`, `tst_res`, `epoll_pwait_init`, `SAFE_SOCKETPAIR`, `epoll_create`, `tst_brk`, `epoll_ctl`, `SAFE_WRITE`, `SAFE_CLOSE`. Relevant structs/types include `struct epoll_event`. Harness metadata uses `.test_all`, `.setup`, `.cleanup`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, pollable descriptor readiness state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<sys/epoll.h>`, `"tst_test.h"`, `"epoll_pwait_var.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `epoll_pwait` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: readiness results depend on descriptor lifetime, nonblocking mode, and timing

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EPOLLIN, EPOLL_CTL_ADD`; harness fields `.test_all, .setup, .cleanup`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_pwait/epoll_pwait02.c -->
