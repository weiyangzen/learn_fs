<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_getparam/sched_getparam01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sched_getparam/sched_getparam01.c

Purpose: Verify that: sched_getparam(2) gets correct scheduling parameters for the specified process: - If pid is zero, sched_getparam(2) gets the scheduling parameters for the calling process. - If pid is not zero, sched_getparam(2) gets the scheduling parameters for the specified [pid] process. In this shard it contributes focused coverage for scheduler parameter retrieval across libc/syscall variants and pid addressing modes.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `verify_sched_getparam`, `setup`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_FORK`, `TST_EXP_PASS_SILENT`, `TST_PASS`, `sched_getparam`, `sched_param`, `sched_priority`, `sched_variant`, `sched_variants`, `setup`, `tst_reap_children`, `tst_res`, `tst_sched`, `tst_test`, `tst_variant`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `verify_sched_getparam`, `setup`.

State and persistence behavior: exercises forked child state. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on `tst_sched` syscall-variant wrappers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: child cleanup and wait ordering matter.

Test signals: pass/fail is reported through TST_EXP_PASS, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_getparam/sched_getparam01.c -->
