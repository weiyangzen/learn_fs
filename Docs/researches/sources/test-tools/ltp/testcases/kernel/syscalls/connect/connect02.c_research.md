<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/connect/connect02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/connect/connect02.c

Purpose: LTP regression coverage for `connect` behavior. Source intent: Copyright (C) 2017 Christoph Paasch <cpaasch@apple.com> Copyright (C) 2020 SUSE LLC <mdoucha@suse.cz> CVE-2018-9568 Test that connect() to AF_UNSPEC address correctly converts IPV6 socket to IPV4 listen socket when IPV6_ADDRFORM is set to AF_INET. Kernel memory corruption fixed in: commit 9d538fa60bad4f7b23193c89e843797a1cf71ef3 Author: Christoph Paasch <cpaasch@apple.com> Date: Tue Sep 26 17:38:50 2017 -0700 net:. The file was read in full for this report (141 lines, 3617 bytes).

Important APIs/types/functions: Primary functions are `setup`, `cleanup`, `run`. Important call/API signals are `connect`, `tst_init_sockaddr_inet6_bin`, `tst_init_sockaddr_inet_bin`, `SAFE_SOCKET`, `SAFE_BIND`, `SAFE_LISTEN`, `SAFE_GETSOCKNAME`, `tst_init_sockaddr_inet`, `SAFE_CLOSE`, `SAFE_CONNECT`, `SAFE_ACCEPT`, `TEST`, `tst_res`, `tst_brk`, `tst_get_connect_address`, `tst_taint_check`. Relevant structs/types include `struct sockaddr_in6`, `struct sockaddr_in`, `struct sockaddr`, `struct sockaddr_storage`, `struct tst_tag`. Harness metadata uses `.test_all`, `.setup`, `.cleanup`, `.tags`, `.taint_check`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, local sockets and network namespace state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<sys/types.h>`, `<sys/socket.h>`, `<netinet/in.h>`, `<netinet/tcp.h>`, `<arpa/inet.h>`, `"tst_test.h"`, `"tst_net.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `connect` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: expected errno and return-value assertions are sensitive to kernel, libc, and architecture ABI differences

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; harness fields `.test_all, .setup, .cleanup, .tags, .taint_check`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/connect/connect02.c -->
