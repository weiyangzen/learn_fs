<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_setscheduler/sched_setscheduler04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sched_setscheduler/sched_setscheduler04.c

Purpose: Testcases that test if sched_setscheduler with flag SCHED_RESET_ON_FORK restores children policy to SCHED_NORMAL. In this shard it contributes focused coverage for scheduler policy mutation, realtime privileges, RLIMIT_NICE, and reset-on-fork behavior.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `test_reset_on_fork`. Key structs/tables: `test_case_t`, `cases`. Important syscall/helper surface includes: `SAFE_FORK`, `TST_CAP`, `TST_CAP_REQ`, `sched_getparam`, `sched_getscheduler`, `sched_param`, `sched_priority`, `sched_setscheduler`, `sched_variant`, `sched_variants`, `tst_cap`, `tst_res`, `tst_sched`, `tst_test`, `tst_variant`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. table-driven cases are held in `cases`. important local functions are `test_reset_on_fork`.

State and persistence behavior: exercises forked child state. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on `tst_sched` syscall-variant wrappers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: child cleanup and wait ordering matter.

Test signals: pass/fail is reported through tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_setscheduler/sched_setscheduler04.c -->
