<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_pwait/epoll_pwait05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/epoll_pwait/epoll_pwait05.c

Purpose: LTP regression coverage for `epoll_pwait` behavior. Source intent: Copyright (c) Huawei Technologies Co., Ltd. Author: Xie Ziyao <xieziyao@huawei.com> \ Verify that, epoll_pwait2() return -1 and set errno to EINVAL with an invalid timespec. The file was read in full for this report (71 lines, 1455 bytes).

Important APIs/types/functions: Primary functions are `run_all`, `setup`, `cleanup`. Important call/API signals are `epoll_pwait2`, `TST_EXP_FAIL`, `epoll_pwait2_supported`, `SAFE_SOCKETPAIR`, `epoll_create`, `tst_brk`, `epoll_ctl`, `SAFE_WRITE`, `SAFE_CLOSE`. Relevant structs/types include `struct epoll_event`, `struct test_case_t`, `struct timespec`. Harness metadata uses `.test`, `.setup`, `.cleanup`, `.tcnt`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run_all`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, kernel clock state or time namespace state, pollable descriptor readiness state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<sys/epoll.h>`, `"tst_test.h"`, `"tst_timer.h"`, `"lapi/epoll.h"`; the modern LTP `struct tst_test` harness; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps. It integrates with the sibling `epoll_pwait` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: readiness results depend on descriptor lifetime, nonblocking mode, and timing

Test signals: explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EINVAL, EPOLLIN, EPOLL_CTL_ADD`; harness fields `.test, .setup, .cleanup, .tcnt`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_pwait/epoll_pwait05.c -->
