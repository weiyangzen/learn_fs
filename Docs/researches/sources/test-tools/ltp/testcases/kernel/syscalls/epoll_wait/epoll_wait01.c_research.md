<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_wait/epoll_wait01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/epoll_wait/epoll_wait01.c

Purpose: LTP regression coverage for `epoll_wait` behavior. Source intent: Copyright (c) 2016 Fujitsu Ltd. Author: Guangwen Feng <fenggw-fnst@cn.fujitsu.com> \ Basic test for epoll_wait. Check that epoll_wait works for EPOLLOUT and EPOLLIN events on an epoll instance and that struct epoll_event is set correctly. The file was read in full for this report (243 lines, 4866 bytes).

Important APIs/types/functions: Primary functions are `get_writesize`, `setup`, `has_event`, `dump_epevs`, `verify_epollout`, `verify_epollin`, `verify_epollio`, `cleanup`, `do_test`. Important call/API signals are `get_writesize`, `SAFE_WRITE`, `tst_brk`, `SAFE_READ`, `tst_res`, `SAFE_PIPE`, `epoll_create`, `epoll_ctl`, `verify_epollout`, `TEST`, `epoll_wait`, `verify_epollin`, `verify_epollio`, `SAFE_CLOSE`. Relevant structs/types include `struct epoll_event`, `struct pollfd`. Harness metadata uses `.test`, `.setup`, `.cleanup`, `.tcnt`.

Control flow: The test is organized around setup-oriented functions `setup`; verify-oriented functions `verify_epollout, verify_epollin, verify_epollio`; test-oriented functions `do_test`; cleanup-oriented functions `cleanup`; do_-oriented functions `do_test`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, pollable descriptor readiness state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<sys/epoll.h>`, `<poll.h>`, `<string.h>`, `<errno.h>`, `"tst_test.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `epoll_wait` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: readiness results depend on descriptor lifetime, nonblocking mode, and timing

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EPOLLOUT, EPOLLIN, EPOLL_CTL_ADD`; harness fields `.test, .setup, .cleanup, .tcnt`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_wait/epoll_wait01.c -->
