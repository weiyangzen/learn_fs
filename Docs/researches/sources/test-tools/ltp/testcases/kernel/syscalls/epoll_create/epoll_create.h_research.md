<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_create/epoll_create.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/epoll_create/epoll_create.h

Purpose: Shared helper/header support for the LTP epoll_create tests. Source intent: Copyright (c) Linux Test Project, 2021 EPOLL_CREATE_H__ The file was read in full for this report (38 lines, 620 bytes).

Important APIs/types/functions: Primary functions are `do_epoll_create`, `variant_info`. Important call/API signals are `do_epoll_create`, `tst_syscall`, `epoll_create`, `tst_res`. Defined constants/macros include `EPOLL_CREATE_H__`, `EPOLL_CREATE_VARIANTS`. The file has little or no explicit LTP harness metadata.

Control flow: The test is organized around do_-oriented functions `do_epoll_create`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, pollable descriptor readiness state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on the local LTP syscall test build environment. It integrates with the sibling `epoll_create` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: permission, umask, setgid, and resource-limit behavior depends on credentials and filesystem mode bits readiness results depend on descriptor lifetime, nonblocking mode, and timing

Test signals: case/errno constants `EPOLL_CREATE_H__, EPOLL_CREATE_VARIANTS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_create/epoll_create.h -->
