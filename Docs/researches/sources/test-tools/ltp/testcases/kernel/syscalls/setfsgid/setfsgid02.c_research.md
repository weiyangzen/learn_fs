<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setfsgid/setfsgid02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setfsgid/setfsgid02.c

Purpose: Testcase for setfsgid() syscall to check that - privileged user can change a filesystem group ID different from saved value of previous setfsgid() call - unprivileged user cannot change it In this shard it contributes focused coverage for filesystem group ID transitions and permission side effects.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `run`, `setup`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_GETPWNAM`, `SAFE_SETEUID`, `SETFSGID`, `TEST`, `TST_RET`, `setfsgid`, `setup`, `tst_res`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `run`, `setup`.

State and persistence behavior: exercises process credentials. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on 16-bit UID/GID compatibility wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners.

Test signals: pass/fail is reported through TST_RET, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setfsgid/setfsgid02.c -->
