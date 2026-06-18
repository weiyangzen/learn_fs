<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_wait/epoll_wait07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/epoll_wait/epoll_wait07.c

Purpose: LTP regression coverage for `epoll_wait` behavior. Source intent: Copyright (C) 2023 SUSE LLC Andrea Cervesato <andrea.cervesato@suse.com> \ Verify that EPOLLONESHOT is correctly handled by epoll_wait. We open a channel, write in it two times and verify that EPOLLIN has been received only once. The file was read in full for this report (72 lines, 1563 bytes).

Important APIs/types/functions: Primary functions are `cleanup`, `run`. Important call/API signals are `SAFE_CLOSE`, `SAFE_PIPE`, `tst_res`, `SAFE_EPOLL_CREATE1`, `SAFE_EPOLL_CTL`, `SAFE_WRITE`, `TST_EXP_EQ_LI`, `SAFE_EPOLL_WAIT`, `SAFE_READ`. Relevant structs/types include `struct epoll_event`. Harness metadata uses `.test_all`, `.cleanup`.

Control flow: The test is organized around run-oriented functions `run`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, pollable descriptor readiness state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<poll.h>`, `<sys/epoll.h>`, `"tst_test.h"`, `"tst_epoll.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `epoll_wait` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: readiness results depend on descriptor lifetime, nonblocking mode, and timing

Test signals: case/errno constants `EPOLLONESHOT, EPOLLIN, EPOLL_CTL_ADD`; harness fields `.test_all, .cleanup`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_wait/epoll_wait07.c -->
