<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_getparam/sched_getparam03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sched_getparam/sched_getparam03.c

Purpose: Verify that, sched_getparam(2) returns -1 and sets errno to - ESRCH if the process with specified pid could not be found - EINVAL if the parameter pid is an invalid value (-1) - EINVAL if the parameter p is an invalid address In this shard it contributes focused coverage for scheduler parameter retrieval across libc/syscall variants and pid addressing modes.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `verify_sched_getparam`, `setup`. Key structs/tables: `test_case_t`. Important syscall/helper surface includes: `TST_EXP_FAIL`, `sched_getparam`, `sched_param`, `sched_variant`, `sched_variants`, `sets`, `setup`, `tst_get_unused_pid`, `tst_res`, `tst_sched`, `tst_test`, `tst_variant`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `verify_sched_getparam`, `setup`.

State and persistence behavior: exercises mostly process-local syscall state with no durable repository state. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on `tst_sched` syscall-variant wrappers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: errno expectations are kernel-version and wrapper-sensitive.

Test signals: pass/fail is reported through TST_EXP_FAIL, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_getparam/sched_getparam03.c -->
