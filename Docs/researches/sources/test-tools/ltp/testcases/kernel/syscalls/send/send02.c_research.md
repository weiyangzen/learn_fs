<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/send/send02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/send/send02.c

Purpose: Check that the kernel correctly handles send()/sendto()/sendmsg() calls with MSG_MORE flag. In this shard it contributes focused coverage for send-family socket error handling and MSG_MORE behavior.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `do_send`, `do_sendto`, `do_sendmsg`, `setup`, `check_recv`, `cleanup`, `run`. Key structs/tables: `test_case`. Important syscall/helper surface includes: `SAFE_ACCEPT`, `SAFE_BIND`, `SAFE_CLOSE`, `SAFE_CONNECT`, `SAFE_GETSOCKNAME`, `SAFE_LISTEN`, `SAFE_SEND`, `SAFE_SENDMSG`, `SAFE_SENDTO`, `SAFE_SOCKET`, `TEST`, `TST_ERR`, `TST_RET`, `sendmsg`, `sendto`, `setup`, `tst_init_sockaddr_inet_bin`, `tst_net`, `tst_res`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `do_send`, `do_sendto`, `do_sendmsg`, `setup`, `check_recv`, `cleanup`, `run`.

State and persistence behavior: exercises socket endpoints or file-transfer descriptors. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on LTP network helpers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: timing-sensitive behavior can be flaky on overloaded systems.

Test signals: pass/fail is reported through TST_RET, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/send/send02.c -->
