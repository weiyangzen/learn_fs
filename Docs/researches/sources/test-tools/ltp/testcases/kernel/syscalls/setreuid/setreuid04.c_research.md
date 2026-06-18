<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setreuid/setreuid04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setreuid/setreuid04.c

Purpose: Verify that root user can change the real and effective uid to an unprivileged user. In this shard it contributes focused coverage for real/effective user ID transitions, saved UID semantics, and file-permission effects.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `run`. Key structs/tables: none explicit. Important syscall/helper surface includes: `GETEUID`, `GETUID`, `SAFE_FORK`, `SAFE_GETPWNAM`, `SETREUID`, `TST_EXP_EQ_LI`, `TST_EXP_PASS`, `setreuid`, `setup`, `tst_reap_children`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setup`, `run`.

State and persistence behavior: exercises forked child state; process credentials. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on 16-bit UID/GID compatibility wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; child cleanup and wait ordering matter; credential mutations must stay isolated to child processes or be restored.

Test signals: pass/fail is reported through TST_EXP_PASS, TST_EXP_EQ. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setreuid/setreuid04.c -->
