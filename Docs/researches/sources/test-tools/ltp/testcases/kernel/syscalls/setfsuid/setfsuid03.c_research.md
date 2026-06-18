<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setfsuid/setfsuid03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setfsuid/setfsuid03.c

Purpose: Verify that setfsuid() correctly updates the filesystem uid when caller is a non-root user and provided fsuid matches caller's real user ID. In this shard it contributes focused coverage for filesystem user ID transitions and permission side effects.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `run`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_GETPWNAM`, `SAFE_GETRESUID`, `SAFE_SETEUID`, `SETFSUID`, `TST_EXP_VAL`, `TST_EXP_VAL_SILENT`, `setfsuid`, `setup`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setup`, `run`.

State and persistence behavior: exercises process credentials. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on 16-bit UID/GID compatibility wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners.

Test signals: pass/fail is reported through TST_EXP_VAL. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setfsuid/setfsuid03.c -->
