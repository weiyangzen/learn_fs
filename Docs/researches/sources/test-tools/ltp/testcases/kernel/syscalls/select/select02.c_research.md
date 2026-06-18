<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/select/select02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/select/select02.c

Purpose: Check that :manpage:`select(2)` timeouts correctly. In this shard it contributes focused coverage for select/pselect ABI variants, fd-set mutation, timeout, EBADF/EFAULT/EINVAL behavior.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `sample_fn`, `setup`, `cleanup`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_CLOSE`, `SAFE_PIPE`, `TEST`, `TST_RET`, `select`, `setup`, `tst_res`, `tst_test`, `tst_timer_sample`, `tst_timer_start`, `tst_timer_stop`, `tst_timer_test`, `tst_us_to_timeval`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `sample_fn`, `setup`, `cleanup`.

State and persistence behavior: exercises mostly process-local syscall state with no durable repository state. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on time64/timer variant helpers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: timing-sensitive behavior can be flaky on overloaded systems.

Test signals: pass/fail is reported through TST_RET, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/select/select02.c -->
