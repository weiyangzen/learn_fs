<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_wait/epoll_wait05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/epoll_wait/epoll_wait05.c

Purpose: LTP regression coverage for `epoll_wait` behavior. Source intent: Copyright (C) 2023 SUSE LLC Andrea Cervesato <andrea.cervesato@suse.com> \ Verify that epoll receives EPOLLRDHUP event when we hang a reading half-socket we are polling on. The file was read in full for this report (125 lines, 2690 bytes).

Important APIs/types/functions: Primary functions are `create_server`, `run`, `setup`, `cleanup`. Important call/API signals are `create_server`, `tst_init_sockaddr_inet_bin`, `SAFE_SOCKET`, `SAFE_BIND`, `SAFE_LISTEN`, `SAFE_GETSOCKNAME`, `tst_res`, `TST_CHECKPOINT_WAKE_AND_WAIT`, `SAFE_CLOSE`, `SAFE_FORK`, `TST_CHECKPOINT_WAIT`, `tst_init_sockaddr_inet`, `SAFE_CONNECT`, `SAFE_EPOLL_CREATE1`, `SAFE_EPOLL_CTL`, `TST_EXP_PASS_SILENT`, `SAFE_EPOLL_WAIT`, `TST_CHECKPOINT_WAKE`, `SAFE_MMAP`, `SAFE_MUNMAP`, `fcntl`. Relevant structs/types include `struct sockaddr_in`, `struct sockaddr`, `struct epoll_event`. Harness metadata uses `.test_all`, `.setup`, `.cleanup`, `.needs_checkpoints`, `.forks_child`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, local sockets and network namespace state, child processes and exit status, pollable descriptor readiness state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `"tst_test.h"`, `"tst_net.h"`, `"tst_epoll.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `epoll_wait` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: readiness results depend on descriptor lifetime, nonblocking mode, and timing

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EPOLLRDHUP, EPOLL_CTL_ADD, F_GETFD`; harness fields `.test_all, .setup, .cleanup, .needs_checkpoints, .forks_child`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_wait/epoll_wait05.c -->
