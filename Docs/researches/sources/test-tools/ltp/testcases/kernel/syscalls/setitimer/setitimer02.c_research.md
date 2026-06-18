<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setitimer/setitimer02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setitimer/setitimer02.c

Purpose: Check that setitimer() call fails: 1. EFAULT with invalid itimerval pointer 2. EINVAL when called with an invalid first argument In this shard it contributes focused coverage for interval timer setup, signal delivery, old kernel itimerval ABI, and errno behavior.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `verify_setitimer`, `setup`. Key structs/tables: none explicit. Important syscall/helper surface includes: `TST_EXP_FAIL`, `setitimer`, `setup`, `tst_buffers`, `tst_test`, `tst_timer`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `verify_setitimer`, `setup`.

State and persistence behavior: exercises interval timers and signals. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on time64/timer variant helpers, LTP syscall-number wrappers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: timing-sensitive behavior can be flaky on overloaded systems; errno expectations are kernel-version and wrapper-sensitive.

Test signals: pass/fail is reported through TST_EXP_FAIL. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setitimer/setitimer02.c -->
