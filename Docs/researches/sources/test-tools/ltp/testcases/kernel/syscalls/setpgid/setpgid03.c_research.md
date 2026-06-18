<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setpgid/setpgid03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setpgid/setpgid03.c

Purpose: Exercises process group mutation, session/exec restrictions, and checkpointed parent-child races. In this shard it contributes focused coverage for process group mutation, session/exec restrictions, and checkpointed parent-child races.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `do_child`, `run`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_EXECLP`, `SAFE_FORK`, `SAFE_SETSID`, `TST_CHECKPOINT_WAIT`, `TST_CHECKPOINT_WAKE`, `TST_CHECKPOINT_WAKE_AND_WAIT`, `TST_EXP_FAIL`, `setpgid`, `setpgid03_child`, `setsid`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `do_child`, `run`.

State and persistence behavior: exercises forked child state. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on standard libc/Linux syscall headers plus LTP assertion and safe-wrapper helpers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: child cleanup and wait ordering matter; errno expectations are kernel-version and wrapper-sensitive.

Test signals: pass/fail is reported through TST_EXP_FAIL. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setpgid/setpgid03.c -->
