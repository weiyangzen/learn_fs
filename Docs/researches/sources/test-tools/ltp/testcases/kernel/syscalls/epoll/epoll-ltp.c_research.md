<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll/epoll-ltp.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/epoll/epoll-ltp.c

Purpose: LTP regression coverage for `epoll` behavior. Source intent: Copyright (c) International Business Machines Corp., 2001 This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version. The file was read in full for this report (739 lines, 22902 bytes).

Important APIs/types/functions: Primary functions are `test_epoll_create`, `test_epoll_ctl`, `main`. Important call/API signals are `tst_old_flush`, `tst_fork`, `waitpid`, `WEXITSTATUS`, `tst_resm`, `epoll_create`, `test_epoll_create`, `close`, `epoll_ctl`, `EPOLL_CTL_TEST_FAIL`, `EPOLL_CTL_TEST_PASS`, `test_epoll_ctl`, `fork`, `epoll`, `tst_brkm`, `tst_exit`. Defined constants/macros include `_GNU_SOURCE`, `TRUE`, `FALSE`, `NUM_RAND_ATTEMPTS`, `BACKING_STORE_SIZE_HINT`, `PROTECT_REGION_START`, `PROTECT_REGION_EXIT`, `PROTECT_REGION_END`, `PROTECT_FUNC`, `RES_PASS`, `RES_FAIL_RETV_MIS_ERRNO_MAT`, `RES_FAIL_RETV_BAD_ERRNO_MAT`, `RES_FAIL_RETV_MAT_ERRNO_MIS`, `RES_FAIL_RETV_BAD_ERRNO_MIS`, `RES_FAIL_RETV_MIS_ERRNO_IGN`, `RES_FAIL_RETV_BAD_ERRNO_IGN`, `RES_PASS_RETV_MAT_ERRNO_IGN`, `EPOLL_CTL_TEST_RESULTS_SHOW_PARAMS`. Relevant structs/types include `struct epoll_event`, `struct timeval`. The file has little or no explicit LTP harness metadata.

Control flow: The test is organized around test-oriented functions `test_epoll_create, test_epoll_ctl`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, child processes and exit status, pollable descriptor readiness state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdio.h>`, `<stdlib.h>`, `<unistd.h>`, `<fcntl.h>`, `<stdarg.h>`, `<string.h>`, `<signal.h>`, `<assert.h>`, `<limits.h>`, `<ctype.h>`; legacy LTP harness APIs. It integrates with the sibling `epoll` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: readiness results depend on descriptor lifetime, nonblocking mode, and timing

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EINVAL, ENOMEM, EPOLL, EPOLLIN, EPOLLOUT, EPOLLPRI, EPOLLERR, EPOLLHUP, EPOLLET, EBADF, EPERM, EPOLL_CTL_TEST_RESULTS_SHOW_PARAMS, EPOLL_CTL_TEST_FAIL, EPOLL_CTL_TEST_PASS, EPOLL_CTL_DEL, EPOLL_CTL_MOD, EPOLL_CTL_ADD`; TCONF skip paths for unsupported kernel, libc, privilege, device, or filesystem conditions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/epoll/epoll-ltp.c -->
