<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_pwait/epoll_pwait_var.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/epoll_pwait/epoll_pwait_var.h

Purpose: Shared helper/header support for the LTP epoll_pwait tests. Source intent: Copyright (c) Huawei Technologies Co., Ltd. Author: Xie Ziyao <xieziyao@huawei.com> LTP_EPOLL_PWAIT_VAR_H The file was read in full for this report (45 lines, 1050 bytes).

Important APIs/types/functions: Primary functions are `do_epoll_pwait`, `epoll_pwait_init`. Important call/API signals are `do_epoll_pwait`, `epoll_pwait2`, `epoll_pwait`, `epoll_pwait_init`, `tst_res`, `epoll_pwait_supported`, `epoll_pwait2_supported`. Defined constants/macros include `LTP_EPOLL_PWAIT_VAR_H`, `TEST_VARIANTS`, `MSEC_PER_SEC`, `NSEC_PER_MSEC`. Relevant structs/types include `struct epoll_event`, `struct timespec`. The file has little or no explicit LTP harness metadata.

Control flow: The test is organized around do_-oriented functions `do_epoll_pwait`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates pollable descriptor readiness state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `"lapi/epoll.h"`; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps. It integrates with the sibling `epoll_pwait` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: readiness results depend on descriptor lifetime, nonblocking mode, and timing

Test signals: return values, errno, and LTP result records are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll_pwait/epoll_pwait_var.h -->
