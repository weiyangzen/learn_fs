<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_setscheduler/sched_setscheduler03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sched_setscheduler/sched_setscheduler03.c

Purpose: nice rlimit ranges from 1 to 40, mapping to real nice value from 19 to -20. We set it to 19, as the default priority of process with fair policy is 120, which will be translated into nice 20, we make this RLIMIT_NICE smaller than that, to verify the can_nice usage issue. In this shard it contributes focused coverage for scheduler policy mutation, realtime privileges, RLIMIT_NICE, and reset-on-fork behavior.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `l_rlimit_show`, `l_rlimit_setup`, `verify_fn`, `setup`, `do_test`. Key structs/tables: `test_case_t`, `cases`. Important syscall/helper surface includes: `SAFE_FORK`, `SAFE_GETPWNAM`, `SAFE_GETRESUID`, `SAFE_GETRLIMIT`, `SAFE_SETEUID`, `SAFE_SETRLIMIT`, `SAFE_WAIT`, `TST_EXP_PASS`, `sched_getscheduler`, `sched_param`, `sched_priority`, `sched_setscheduler`, `sched_variant`, `sched_variants`, `seteuid`, `setup`, `tst_brk`, `tst_res`, `tst_sched`, `tst_test`, `tst_variant`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. table-driven cases are held in `cases`. important local functions are `l_rlimit_show`, `l_rlimit_setup`, `verify_fn`, `setup`, `do_test`.

State and persistence behavior: exercises forked child state; process credentials; resource limits. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on `tst_sched` syscall-variant wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; child cleanup and wait ordering matter; credential mutations must stay isolated to child processes or be restored.

Test signals: pass/fail is reported through TST_EXP_PASS, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_setscheduler/sched_setscheduler03.c -->
