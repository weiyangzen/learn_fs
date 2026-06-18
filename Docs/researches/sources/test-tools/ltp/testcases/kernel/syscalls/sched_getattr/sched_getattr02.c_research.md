<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_getattr/sched_getattr02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sched_getattr/sched_getattr02.c

Purpose: Verify that, sched_getattr(2) returns -1 and sets errno to: 1. ESRCH if pid is unused. 2. EINVAL if address is NULL. 3. EINVAL if size is invalid. 4. EINVAL if flag is not zero. In this shard it contributes focused coverage for scheduler attribute syscall validation around sched_attr size, flags, and pid lookup.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `verify_sched_getattr`, `setup`. Key structs/tables: `test_case`. Important syscall/helper surface includes: `TST_EXP_FAIL`, `sched_attr`, `sched_getattr`, `sets`, `setup`, `tst_get_unused_pid`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `verify_sched_getattr`, `setup`.

State and persistence behavior: exercises temporary files or descriptors. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on standard libc/Linux syscall headers plus LTP assertion and safe-wrapper helpers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: errno expectations are kernel-version and wrapper-sensitive.

Test signals: pass/fail is reported through TST_EXP_FAIL. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_getattr/sched_getattr02.c -->
