<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setresuid/setresuid02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setresuid/setresuid02.c

Purpose: Test that a non-root user can change the real, effective and saved uid values through the setresuid system call. In this shard it contributes focused coverage for real/effective/saved user ID transitions and file-permission effects.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `run`. Key structs/tables: `test_data_t`. Important syscall/helper surface includes: `SAFE_GETPWNAM`, `SAFE_SETRESUID`, `SETRESUID`, `TST_EXP_PASS_SILENT`, `TST_PASS`, `setresuid`, `setup`, `tst_check_resuid`, `tst_get_uids`, `tst_res`, `tst_test`, `tst_uid`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setup`, `run`.

State and persistence behavior: exercises process credentials. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on 16-bit UID/GID compatibility wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; credential mutations must stay isolated to child processes or be restored.

Test signals: pass/fail is reported through TST_EXP_PASS, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setresuid/setresuid02.c -->
