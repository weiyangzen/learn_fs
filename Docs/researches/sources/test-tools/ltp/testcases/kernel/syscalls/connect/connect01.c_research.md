<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/connect/connect01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/connect/connect01.c

Purpose: LTP regression coverage for `connect` behavior. Source intent: Copyright (c) International Business Machines Corp., 2001 This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version. The file was read in full for this report (309 lines, 7710 bytes).

Important APIs/types/functions: Primary functions are `setup`, `start_server`, `sys_connect`, `main`, `cleanup`, `setup0`, `cleanup0`, `setup1`, `cleanup1`, `setup2`, `do_child`. Important call/API signals are `connect`, `sys_connect`, `tst_syscall`, `tst_parse_opts`, `TEST_LOOPING`, `TEST`, `tst_resm`, `tst_exit`, `TST_GET_UNUSED_PORT`, `open`, `tst_brkm`, `close`, `SAFE_SOCKET`, `SAFE_CONNECT`, `socket`, `bind`, `listen`, `SAFE_GETSOCKNAME`, `tst_fork`, `accept`, `read`. Defined constants/macros include `connect`. Relevant structs/types include `struct sockaddr_in`, `struct test_case_t`, `struct sockaddr`. The file has little or no explicit LTP harness metadata.

Control flow: The test is organized around setup-oriented functions `setup, setup0, setup1, setup2`; cleanup-oriented functions `cleanup, cleanup0, cleanup1`; child-oriented functions `do_child`; do_-oriented functions `do_child`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, local sockets and network namespace state, child processes and exit status. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdio.h>`, `<unistd.h>`, `<errno.h>`, `<fcntl.h>`, `<sys/types.h>`, `<sys/socket.h>`, `<sys/signal.h>`, `<sys/un.h>`, `<netinet/in.h>`, `"test.h"`; legacy LTP harness APIs; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps. It integrates with the sibling `connect` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: expected errno and return-value assertions are sensitive to kernel, libc, and architecture ABI differences

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EBADF, EFAULT, EINVAL, ENOTSOCK, EISCONN, ECONNREFUSED, EAFNOSUPPORT, EINTR, O_WRONLY`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/connect/connect01.c -->
