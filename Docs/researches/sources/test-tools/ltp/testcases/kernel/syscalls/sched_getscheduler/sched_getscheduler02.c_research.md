<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_getscheduler/sched_getscheduler02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sched_getscheduler/sched_getscheduler02.c

Purpose: Pass an unused pid to sched_getscheduler() and test for ESRCH. In this shard it contributes focused coverage for scheduler policy readback and error handling after policy changes.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `run`. Key structs/tables: none explicit. Important syscall/helper surface includes: `TST_EXP_FAIL`, `sched_getscheduler`, `sched_variant`, `sched_variants`, `setup`, `tst_get_unused_pid`, `tst_res`, `tst_sched`, `tst_test`, `tst_variant`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setup`, `run`.

State and persistence behavior: exercises mostly process-local syscall state with no durable repository state. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on `tst_sched` syscall-variant wrappers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: errno expectations are kernel-version and wrapper-sensitive.

Test signals: pass/fail is reported through TST_EXP_FAIL, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_getscheduler/sched_getscheduler02.c -->
