<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setpgid/setpgid01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setpgid/setpgid01.c

Purpose: Verify basic setpgid() functionality, re-setting group ID inside both parent and child. In the first case, we obtain getpgrp() and set it. In the second case, we use setpgid(0, 0). In this shard it contributes focused coverage for process group mutation, session/exec restrictions, and checkpointed parent-child races.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setpgid_test1`, `setpgid_test2`, `run`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_FORK`, `TST_EXP_EQ_LI`, `TST_EXP_PASS`, `TST_EXP_PID`, `setpgid`, `setpgid_test1`, `setpgid_test2`, `setting`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setpgid_test1`, `setpgid_test2`, `run`.

State and persistence behavior: exercises forked child state. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on standard libc/Linux syscall headers plus LTP assertion and safe-wrapper helpers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: child cleanup and wait ordering matter.

Test signals: pass/fail is reported through TST_EXP_PASS, TST_EXP_EQ. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setpgid/setpgid01.c -->
