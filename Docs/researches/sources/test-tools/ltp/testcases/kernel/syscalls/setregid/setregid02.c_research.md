<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setregid/setregid02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setregid/setregid02.c

Purpose: Test that setregid() fails and sets the proper errno values when a non-root user attemps to change the real or effective group id to a value other than the current gid or the current effective gid. In this shard it contributes focused coverage for real/effective group ID transitions and saved-id semantics.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `gid_verify`, `run`, `setup`. Key structs/tables: `tcase`. Important syscall/helper surface includes: `SAFE_GETPWNAM`, `SAFE_SETGID`, `SAFE_SETUID`, `SETREGID`, `TEST`, `TST_ERR`, `TST_RET`, `setregid`, `sets`, `setup`, `tst_get_gids`, `tst_res`, `tst_strerrno`, `tst_test`, `tst_uid`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `gid_verify`, `run`, `setup`.

State and persistence behavior: exercises process credentials. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on 16-bit UID/GID compatibility wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners.

Test signals: pass/fail is reported through TST_RET, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setregid/setregid02.c -->
