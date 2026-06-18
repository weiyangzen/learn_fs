<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_create/epoll_create01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/epoll_create/epoll_create01.c

Purpose: LTP regression coverage for `epoll_create` behavior. Source intent: Copyright (c) Linux Test Project, 2021 Author: Xie Ziyao <ziyaoxie@outlook.com> \ Verify that epoll_create return a nonnegative file descriptor on success. The size argument informed the kernel of the number of file descriptors that the caller expected to add to the epoll instance, but it is no longer required. The file was read in full for this report (38 lines, 839 bytes).

Important APIs/types/functions: Primary functions are `run`. Important call/API signals are `TST_EXP_FD`, `do_epoll_create`, `epoll_create`, `SAFE_CLOSE`. Harness metadata uses `.test`, `.setup`, `.tcnt`.

Control flow: The test is organized around run-oriented functions `run`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, pollable descriptor readiness state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<sys/epoll.h>`, `"tst_test.h"`, `"lapi/epoll.h"`, `"lapi/syscalls.h"`, `"epoll_create.h"`; the modern LTP `struct tst_test` harness; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps. It integrates with the sibling `epoll_create` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: permission, umask, setgid, and resource-limit behavior depends on credentials and filesystem mode bits readiness results depend on descriptor lifetime, nonblocking mode, and timing

Test signals: case/errno constants `EPOLL_CREATE_VARIANTS`; harness fields `.test, .setup, .tcnt`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_create/epoll_create01.c -->
