<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendmmsg/sendmmsg02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sendmmsg/sendmmsg02.c

Purpose: Exercises batched datagram send syscall wrappers and time64 variant coverage. In this shard it contributes focused coverage for batched datagram send syscall wrappers and time64 variant coverage.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `do_test`, `setup`, `cleanup`. Key structs/tables: `test_case`, `tcase`. Important syscall/helper surface includes: `SAFE_CLOSE`, `SAFE_SOCKET`, `TST_EXP_FAIL`, `sendmmsg`, `setup`, `tst_buffers`, `tst_res`, `tst_test`, `tst_variant`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. table-driven cases are held in `tcase`. important local functions are `do_test`, `setup`, `cleanup`.

State and persistence behavior: exercises socket endpoints or file-transfer descriptors. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on time64/timer variant helpers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: errno expectations are kernel-version and wrapper-sensitive.

Test signals: pass/fail is reported through TST_EXP_FAIL, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendmmsg/sendmmsg02.c -->
