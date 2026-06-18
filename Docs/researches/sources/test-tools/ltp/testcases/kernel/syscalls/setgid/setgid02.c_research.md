<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setgid/setgid02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setgid/setgid02.c

Purpose: Test if setgid() system call sets errno to EPERM correctly. [Algorithm] Call setgid() to set the gid to that of root. Run this test as nobody, and expect to get EPERM. In this shard it contributes focused coverage for real/effective group ID setting and EPERM handling.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `run`, `setup`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_GETPWNAM`, `SAFE_SETGID`, `SAFE_SETUID`, `SETGID`, `TST_EXP_FAIL`, `setgid`, `sets`, `setup`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `run`, `setup`.

State and persistence behavior: exercises process credentials. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on 16-bit UID/GID compatibility wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; errno expectations are kernel-version and wrapper-sensitive.

Test signals: pass/fail is reported through TST_EXP_FAIL. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setgid/setgid02.c -->
