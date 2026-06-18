<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setpriority/setpriority02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setpriority/setpriority02.c

Purpose: Verify that, 1) setpriority(2) fails with -1 and sets errno to EINVAL if 'which' argument was not one of PRIO_PROCESS, PRIO_PGRP, or PRIO_USER. 2) setpriority(2) fails with -1 and sets errno to ESRCH if no process was located for 'which' and 'who' arguments. 3) setpriority(2) fails with -1 and sets errno to EACCES if an unprivileged user attempted to lower a process priority. 4) setpriority(2) fails with -1 and sets errno to EPERM if an unprivileged user attempted to change a process which ID is different from the test process. In this shard it contributes focused coverage for nice priority setting by process, process group, and user plus permission errors.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setpriority_test`, `verify_setpriority`, `setup`. Key structs/tables: `tcase`. Important syscall/helper surface includes: `SAFE_FORK`, `SAFE_GETPWNAM`, `SAFE_SETPGID`, `SAFE_SETUID`, `TEST`, `TST_ERR`, `TST_RET`, `setpriority`, `setpriority_test`, `sets`, `setup`, `tst_reap_children`, `tst_res`, `tst_strerrno`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setpriority_test`, `verify_setpriority`, `setup`.

State and persistence behavior: exercises forked child state. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; child cleanup and wait ordering matter.

Test signals: pass/fail is reported through TST_RET, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setpriority/setpriority02.c -->
