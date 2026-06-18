<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_rr_get_interval/sched_rr_get_interval03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sched_rr_get_interval/sched_rr_get_interval03.c

Purpose: Verify that: - sched_rr_get_interval() fails with errno set to EINVAL for an invalid pid - sched_rr_get_interval() fails with errno set to ESRCH if the process with specified pid does not exists - sched_rr_get_interval() fails with errno set to EFAULT if the address specified as &tp is invalid In this shard it contributes focused coverage for round-robin interval reporting across libc, old timespec, and time64 syscall variants.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `run`. Key structs/tables: `test_cases_t`, `variants`. Important syscall/helper surface includes: `TST_EXP_FAIL`, `TST_KERN_OLD_TIMESPEC`, `TST_KERN_TIMESPEC`, `TST_LIBC_TIMESPEC`, `sched_param`, `sched_rr_get_interval`, `sched_setscheduler`, `setup`, `tst_check_rt_group_sched_support`, `tst_get_bad_addr`, `tst_get_unused_pid`, `tst_res`, `tst_sched`, `tst_test`, `tst_timer`, `tst_ts`, `tst_ts_get`, `tst_variant`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. table-driven cases are held in `variants`. important local functions are `setup`, `run`.

State and persistence behavior: exercises mostly process-local syscall state with no durable repository state. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on `tst_sched` syscall-variant wrappers, time64/timer variant helpers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; timing-sensitive behavior can be flaky on overloaded systems; errno expectations are kernel-version and wrapper-sensitive.

Test signals: pass/fail is reported through TST_EXP_FAIL, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_rr_get_interval/sched_rr_get_interval03.c -->
