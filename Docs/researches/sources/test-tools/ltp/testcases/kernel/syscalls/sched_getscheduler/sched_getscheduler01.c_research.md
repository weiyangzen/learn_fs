<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_getscheduler/sched_getscheduler01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sched_getscheduler/sched_getscheduler01.c

Purpose: Testcase to check sched_getscheduler() returns correct return value. [Algorithm] Call sched_setcheduler() to set the scheduling policy of the current process. Then call sched_getscheduler() to ensure that this is same as what set by the previous call to sched_setscheduler(). Use SCHED_RR, SCHED_FIFO, SCHED_OTHER as the scheduling policies for sched_setscheduler(). In this shard it contributes focused coverage for scheduler policy readback and error handling after policy changes.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `run`, `setup`. Key structs/tables: `test_cases_t`. Important syscall/helper surface includes: `TEST`, `TST_EXP_PASS_SILENT`, `TST_PASS`, `TST_RET`, `sched_getscheduler`, `sched_param`, `sched_priority`, `sched_setcheduler`, `sched_setscheduler`, `sched_variant`, `sched_variants`, `setup`, `tst_check_rt_group_sched_support`, `tst_res`, `tst_sched`, `tst_test`, `tst_variant`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `run`, `setup`.

State and persistence behavior: exercises mostly process-local syscall state with no durable repository state. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on `tst_sched` syscall-variant wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners.

Test signals: pass/fail is reported through TST_EXP_PASS, TST_RET, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_getscheduler/sched_getscheduler01.c -->
