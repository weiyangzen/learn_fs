<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendfile/sendfile08.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sendfile/sendfile08.c

Purpose: Bug in the splice code has caused the file position on the write side of the sendfile system call to be incorrectly set to the read side file position. This can result in the data being written to an incorrect offset. This is a regression test for kernel commit 2cb4b05e76478. In this shard it contributes focused coverage for sendfile data transfer, offset, large-file, nonblocking, and regression coverage.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `run`, `setup`, `cleanup`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_CLOSE`, `SAFE_CREAT`, `SAFE_LSEEK`, `SAFE_OPEN`, `SAFE_READ`, `SAFE_WRITE`, `SAFE_WRITE_ALL`, `TEST`, `TST_RET`, `sendfile`, `setup`, `tst_brk`, `tst_res`, `tst_tag`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `run`, `setup`, `cleanup`.

State and persistence behavior: exercises temporary files or descriptors; socket endpoints or file-transfer descriptors. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on standard libc/Linux syscall headers plus LTP assertion and safe-wrapper helpers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: regression tags tie behavior to specific kernel fixes.

Test signals: pass/fail is reported through TST_RET, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendfile/sendfile08.c -->
