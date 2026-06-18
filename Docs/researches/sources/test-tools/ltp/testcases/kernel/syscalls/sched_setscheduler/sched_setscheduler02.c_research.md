<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_setscheduler/sched_setscheduler02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sched_setscheduler/sched_setscheduler02.c

Purpose: Testcase to test whether sched_setscheduler(2) sets the errnos correctly. [Algorithm] Call sched_setscheduler as a non-root uid, and expect EPERM to be returned. In this shard it contributes focused coverage for scheduler policy mutation, realtime privileges, RLIMIT_NICE, and reset-on-fork behavior.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `run`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_FORK`, `SAFE_GETPWNAM`, `SAFE_SETEUID`, `TST_EXP_FAIL`, `sched_param`, `sched_priority`, `sched_setscheduler`, `sched_variant`, `sched_variants`, `sets`, `setup`, `tst_reap_children`, `tst_res`, `tst_sched`, `tst_test`, `tst_variant`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setup`, `run`.

State and persistence behavior: exercises forked child state. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on `tst_sched` syscall-variant wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; child cleanup and wait ordering matter; errno expectations are kernel-version and wrapper-sensitive.

Test signals: pass/fail is reported through TST_EXP_FAIL, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_setscheduler/sched_setscheduler02.c -->
