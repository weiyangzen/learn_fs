<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setegid/setegid02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setegid/setegid02.c

Purpose: Verify that setegid() fails with EPERM when the calling process is not privileged and egid does not match the current real group ID, current effective group ID, or current saved set-group-ID. In this shard it contributes focused coverage for effective group ID update behavior for privileged and unprivileged callers.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `setegid_verify`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_GETPWNAM`, `SAFE_SETEUID`, `TST_EXP_FAIL`, `setegid`, `setegid_verify`, `setup`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setup`, `setegid_verify`.

State and persistence behavior: exercises process credentials. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; errno expectations are kernel-version and wrapper-sensitive.

Test signals: pass/fail is reported through TST_EXP_FAIL. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setegid/setegid02.c -->
