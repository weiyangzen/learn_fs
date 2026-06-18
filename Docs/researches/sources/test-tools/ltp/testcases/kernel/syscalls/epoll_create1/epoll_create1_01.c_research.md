<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_create1/epoll_create1_01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/epoll_create1/epoll_create1_01.c

Purpose: LTP regression coverage for `epoll_create1` behavior. Source intent: Copyright (c) Ulrich Drepper <drepper@redhat.com> Copyright (c) International Business Machines Corp., 2009 \ Verify that epoll_create1 sets the close-on-exec flag for the returned file descriptor with EPOLL_CLOEXEC. The file was read in full for this report (48 lines, 1011 bytes).

Important APIs/types/functions: Primary functions are `run`. Important call/API signals are `tst_syscall`, `tst_brk`, `epoll_create1`, `SAFE_FCNTL`, `tst_res`, `SAFE_CLOSE`. Relevant structs/types include `struct test_case_t`. Harness metadata uses `.test`, `.tcnt`.

Control flow: The test is organized around run-oriented functions `run`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, pollable descriptor readiness state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<sys/epoll.h>`, `"tst_test.h"`, `"lapi/epoll.h"`, `"lapi/syscalls.h"`; the modern LTP `struct tst_test` harness; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps. It integrates with the sibling `epoll_create1` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: permission, umask, setgid, and resource-limit behavior depends on credentials and filesystem mode bits readiness results depend on descriptor lifetime, nonblocking mode, and timing

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EPOLL_CLOEXEC, F_GETFD, FD_CLOEXEC`; harness fields `.test, .tcnt`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_create1/epoll_create1_01.c -->
