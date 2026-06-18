<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_pwait/epoll_pwait01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/epoll_pwait/epoll_pwait01.c

Purpose: LTP regression coverage for `epoll_pwait` behavior. Source intent: Copyright (c) 2016 Fujitsu Ltd. Author: Guangwen Feng <fenggw-fnst@cn.fujitsu.com> Copyright (c) 2021 Xie Ziyao <xieziyao@huawei.com> \ Basic test for epoll_pwait() and epoll_pwait2(). The file was read in full for this report (117 lines, 2434 bytes).

Important APIs/types/functions: Primary functions are `sighandler`, `verify_sigmask`, `verify_nonsigmask`, `run`, `setup`, `cleanup`. Important call/API signals are `epoll_pwait`, `epoll_pwait2`, `TEST`, `do_epoll_pwait`, `tst_res`, `TST_EXP_FAIL`, `SAFE_FORK`, `TST_PROCESS_STATE_WAIT`, `SAFE_KILL`, `SAFE_WRITE`, `SAFE_READ`, `tst_reap_children`, `epoll_pwait_init`, `SAFE_SIGEMPTYSET`, `SAFE_SIGADDSET`, `SAFE_SIGACTION`, `SAFE_SOCKETPAIR`, `epoll_create`, `tst_brk`, `epoll_ctl`, `SAFE_CLOSE`. Relevant structs/types include `struct epoll_event`, `struct sigaction`. Harness metadata uses `.test`, `.setup`, `.cleanup`, `.tcnt`, `.forks_child`.

Control flow: The test is organized around setup-oriented functions `setup`; verify-oriented functions `verify_sigmask, verify_nonsigmask`; run-oriented functions `run`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, child processes and exit status, pollable descriptor readiness state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdlib.h>`, `<sys/epoll.h>`, `"tst_test.h"`, `"epoll_pwait_var.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `epoll_pwait` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: readiness results depend on descriptor lifetime, nonblocking mode, and timing

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EINTR, EPOLLIN, EPOLL_CTL_ADD`; harness fields `.test, .setup, .cleanup, .tcnt, .forks_child`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_pwait/epoll_pwait01.c -->
