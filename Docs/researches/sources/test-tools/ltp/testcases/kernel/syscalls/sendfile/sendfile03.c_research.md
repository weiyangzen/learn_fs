<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendfile/sendfile03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sendfile/sendfile03.c

Purpose: Testcase to test that sendfile(2) system call returns EBADF when passing wrong out_fd or in_fd. There are four cases: - in_fd == -1 - out_fd = -1 - in_fd opened with O_WRONLY - out_fd opened with O_RDONLY In this shard it contributes focused coverage for sendfile data transfer, offset, large-file, nonblocking, and regression coverage.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `cleanup`, `run`. Key structs/tables: `test_case_t`. Important syscall/helper surface includes: `SAFE_CLOSE`, `SAFE_CREAT`, `SAFE_OPEN`, `TST_EXP_FAIL2`, `sendfile`, `setup`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setup`, `cleanup`, `run`.

State and persistence behavior: exercises temporary files or descriptors; socket endpoints or file-transfer descriptors. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on standard libc/Linux syscall headers plus LTP assertion and safe-wrapper helpers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: errno expectations are kernel-version and wrapper-sensitive.

Test signals: pass/fail is reported through TST_EXP_FAIL. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendfile/sendfile03.c -->
