<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_setparam/sched_setparam03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sched_setparam/sched_setparam03.c

Purpose: Checks functionality for sched_setparam(2) for pid != 0 This test forks a child and changes its parent's scheduling priority. In this shard it contributes focused coverage for scheduler priority update semantics for current, parent, and unauthorized processes.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `run`, `setup`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_FORK`, `TST_EXP_PASS_SILENT`, `sched_getparam`, `sched_param`, `sched_priority`, `sched_setparam`, `sched_setscheduler`, `sched_variant`, `sched_variants`, `setup`, `tst_brk`, `tst_check_rt_group_sched_support`, `tst_reap_children`, `tst_res`, `tst_sched`, `tst_test`, `tst_variant`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `run`, `setup`.

State and persistence behavior: exercises forked child state. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on `tst_sched` syscall-variant wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; child cleanup and wait ordering matter.

Test signals: pass/fail is reported through TST_EXP_PASS, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_setparam/sched_setparam03.c -->
