<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendmmsg/sendmmsg01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sendmmsg/sendmmsg01.c

Purpose: Basic sendmmsg() test that sends and receives messages. This test is based on source contained in the man pages for sendmmsg and recvmmsg in release 4.15 of the Linux man-pages project. In this shard it contributes focused coverage for batched datagram send syscall wrappers and time64 variant coverage.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `run`, `setup`, `cleanup`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_BIND`, `SAFE_CLOSE`, `SAFE_CONNECT`, `SAFE_SOCKET`, `TST_GET_UNUSED_PORT`, `sendmmsg`, `setup`, `tst_buffers`, `tst_res`, `tst_test`, `tst_ts`, `tst_ts_get`, `tst_ts_set_nsec`, `tst_ts_set_sec`, `tst_variant`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `run`, `setup`, `cleanup`.

State and persistence behavior: exercises socket endpoints or file-transfer descriptors. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on time64/timer variant helpers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: main risk is false pass/fail if the surrounding harness changes syscall wrappers or expected errno semantics.

Test signals: pass/fail is reported through tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendmmsg/sendmmsg01.c -->
