<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setgroups/setgroups03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setgroups/setgroups03.c

Purpose: Test for EINVAL, EPERM, EFAULT errors. - setgroups() fails with EINVAL if the size argument value is > NGROUPS. - setgroups() fails with EPERM if the calling process is not super-user. - setgroups() fails with EFAULT if the list has an invalid address. In this shard it contributes focused coverage for supplementary group list setting, bounds, privilege, and bad-pointer validation.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `verify_setgroups`, `setup`. Key structs/tables: `tcase`. Important syscall/helper surface includes: `SAFE_GETPWNAM`, `SAFE_SETEUID`, `SETGROUPS`, `TST_EXP_FAIL`, `setgroups`, `setup`, `tst_buffers`, `tst_get_bad_addr`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `verify_setgroups`, `setup`.

State and persistence behavior: exercises process credentials. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on 16-bit UID/GID compatibility wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; errno expectations are kernel-version and wrapper-sensitive.

Test signals: pass/fail is reported through TST_EXP_FAIL. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setgroups/setgroups03.c -->
