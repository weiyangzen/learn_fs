<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setresgid/setresgid02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setresgid/setresgid02.c

Purpose: Verify that setresgid() will successfully set the expected GID when called by root with the following combinations of arguments: - setresgid(-1, -1, -1) - setresgid(-1, -1, other) - setresgid(-1, other, -1) - setresgid(other, -1, -1) - setresgid(root, root, root) - setresgid(root, main, main) In this shard it contributes focused coverage for real/effective/saved group ID transitions and filesystem GID coupling.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `run`. Key structs/tables: `test_case_t`, `test_cases`. Important syscall/helper surface includes: `SAFE_SETRESGID`, `SETRESGID`, `TST_EXP_PASS_SILENT`, `TST_PASS`, `setresgid`, `setup`, `tst_check_resgid`, `tst_get_gids`, `tst_res`, `tst_test`, `tst_uid`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. table-driven cases are held in `test_cases`. important local functions are `setup`, `run`.

State and persistence behavior: exercises process credentials. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on 16-bit UID/GID compatibility wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners.

Test signals: pass/fail is reported through TST_EXP_PASS, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setresgid/setresgid02.c -->
