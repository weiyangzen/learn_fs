<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setitimer/setitimer01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setitimer/setitimer01.c

Purpose: Spawn a child, verify that setitimer() syscall passes and it ends up counting inside expected boundaries. Then verify from the parent that the syscall sent the correct signal to the child. In this shard it contributes focused coverage for interval timer setup, signal delivery, old kernel itimerval ABI, and errno behavior.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `sig_routine`, `set_setitimer_value`, `verify_setitimer`, `setup`. Key structs/tables: `tcase`. Important syscall/helper surface includes: `SAFE_CLOCK_GETRES`, `SAFE_FORK`, `SAFE_SIGNAL`, `SAFE_WAITPID`, `TST_EXP_EQ_LI`, `TST_EXP_PASS`, `set_setitimer_value`, `setitimer`, `setup`, `tst_brk`, `tst_buffers`, `tst_no_corefile`, `tst_res`, `tst_safe_clocks`, `tst_strsig`, `tst_strstatus`, `tst_test`, `tst_timer`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `sig_routine`, `set_setitimer_value`, `verify_setitimer`, `setup`.

State and persistence behavior: exercises forked child state; interval timers and signals. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on time64/timer variant helpers, LTP syscall-number wrappers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: child cleanup and wait ordering matter; timing-sensitive behavior can be flaky on overloaded systems.

Test signals: pass/fail is reported through TST_EXP_PASS, TST_EXP_EQ, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setitimer/setitimer01.c -->
