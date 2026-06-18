<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_wait/epoll_wait03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/epoll_wait/epoll_wait03.c

Purpose: LTP regression coverage for `epoll_wait` behavior. Source intent: Copyright (c) 2016 Fujitsu Ltd. Author: Guangwen Feng <fenggw-fnst@cn.fujitsu.com> Copyright (c) 2021 Xie Ziyao <xieziyao@huawei.com> \ Basic test for epoll_wait: - epoll_wait fails with EBADF if epfd is not a valid file descriptor. - epoll_wait fails with EINVAL if epfd is not an epoll file descriptor. The file was read in full for this report (85 lines, 2160 bytes).

Important APIs/types/functions: Primary functions are `setup`, `verify_epoll_wait`, `cleanup`. Important call/API signals are `SAFE_MMAP`, `SAFE_PIPE`, `epoll_create`, `tst_brk`, `epoll_ctl`, `verify_epoll_wait`, `TST_EXP_FAIL`, `epoll_wait`, `SAFE_CLOSE`. Relevant structs/types include `struct epoll_event`, `struct test_case_t`. Harness metadata uses `.test`, `.setup`, `.cleanup`, `.tcnt`.

Control flow: The test is organized around setup-oriented functions `setup`; verify-oriented functions `verify_epoll_wait`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, pollable descriptor readiness state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<sys/mman.h>`, `<sys/epoll.h>`, `"tst_test.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `epoll_wait` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: readiness results depend on descriptor lifetime, nonblocking mode, and timing

Test signals: explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EBADF, EINVAL, EFAULT, EPOLLOUT, EPOLL_CTL_ADD`; harness fields `.test, .setup, .cleanup, .tcnt`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_wait/epoll_wait03.c -->
