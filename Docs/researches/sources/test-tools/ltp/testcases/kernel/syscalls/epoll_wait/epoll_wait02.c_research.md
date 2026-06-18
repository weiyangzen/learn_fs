<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_wait/epoll_wait02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/epoll_wait/epoll_wait02.c

Purpose: LTP regression coverage for `epoll_wait` behavior. Source intent: Copyright (c) 2016 Fujitsu Ltd. Author: Guangwen Feng <fenggw-fnst@cn.fujitsu.com> Copyright (c) 2017 Cyril Hrubis <chrubis@suse.cz> \ Check that epoll_wait(2) timeouts correctly. The file was read in full for this report (72 lines, 1297 bytes).

Important APIs/types/functions: Primary functions are `sample_fn`, `setup`, `cleanup`. Important call/API signals are `epoll_wait`, `tst_timer_start`, `TEST`, `tst_timer_stop`, `tst_timer_sample`, `tst_res`, `SAFE_PIPE`, `epoll_create`, `tst_brk`, `epoll_ctl`, `SAFE_CLOSE`. Relevant structs/types include `struct epoll_event`. Harness metadata uses `.setup`, `.cleanup`.

Control flow: The test is organized around setup-oriented functions `setup`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, kernel clock state or time namespace state, pollable descriptor readiness state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<sys/epoll.h>`, `<unistd.h>`, `<errno.h>`, `"tst_timer_test.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `epoll_wait` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: readiness results depend on descriptor lifetime, nonblocking mode, and timing

Test signals: explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EPOLLIN, EPOLL_CTL_ADD`; harness fields `.setup, .cleanup`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_wait/epoll_wait02.c -->
