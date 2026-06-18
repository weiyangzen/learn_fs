<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendfile/sendfile02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sendfile/sendfile02.c

Purpose: Test the basic functionality of the sendfile() system call: 1. Call sendfile() with offset = 0. 2. Call sendfile() with offset in the middle of the file. In this shard it contributes focused coverage for sendfile data transfer, offset, large-file, nonblocking, and regression coverage.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `run`. Key structs/tables: `test_case_t`. Important syscall/helper surface includes: `SAFE_CLOSE`, `SAFE_CREAT`, `SAFE_LSEEK`, `SAFE_OPEN`, `SAFE_WRITE`, `SAFE_WRITE_ALL`, `TEST`, `TST_RET`, `sendfile`, `setup`, `tst_res`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setup`, `run`.

State and persistence behavior: exercises temporary files or descriptors; socket endpoints or file-transfer descriptors. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on standard libc/Linux syscall headers plus LTP assertion and safe-wrapper helpers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: main risk is false pass/fail if the surrounding harness changes syscall wrappers or expected errno semantics.

Test signals: pass/fail is reported through TST_RET, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendfile/sendfile02.c -->
