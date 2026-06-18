<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setpgid/setpgid02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setpgid/setpgid02.c

Purpose: Verify that setpgid(2) syscall fails with: - EINVAL when given pgid is less than 0. - ESRCH when pid is not the calling process and not a child of the calling process. - EPERM when an attempt was made to move a process into a nonexisting process group. In this shard it contributes focused coverage for process group mutation, session/exec restrictions, and checkpointed parent-child races.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `run`. Key structs/tables: `tcase`. Important syscall/helper surface includes: `SAFE_FILE_SCANF`, `TST_EXP_FAIL`, `setpgid`, `setup`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setup`, `run`.

State and persistence behavior: exercises mostly process-local syscall state with no durable repository state. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on standard libc/Linux syscall headers plus LTP assertion and safe-wrapper helpers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: errno expectations are kernel-version and wrapper-sensitive.

Test signals: pass/fail is reported through TST_EXP_FAIL. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setpgid/setpgid02.c -->
