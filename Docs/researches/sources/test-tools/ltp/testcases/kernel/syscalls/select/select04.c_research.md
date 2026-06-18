<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/select/select04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/select/select04.c

Purpose: Test to check if fd set bits are cleared by :manpage:`select(2)`. [Algorithm] - Check that writefds flag is cleared on full pipe - Check that readfds flag is cleared on empty pipe In this shard it contributes focused coverage for select/pselect ABI variants, fd-set mutation, timeout, EBADF/EFAULT/EINVAL behavior.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `run`, `setup`. Key structs/tables: `tcases`. Important syscall/helper surface includes: `SAFE_PIPE`, `SAFE_PIPE2`, `TEST`, `TST_ERR`, `TST_RET`, `select`, `setup`, `tst_res`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `run`, `setup`.

State and persistence behavior: exercises temporary files or descriptors. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on standard libc/Linux syscall headers plus LTP assertion and safe-wrapper helpers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: main risk is false pass/fail if the surrounding harness changes syscall wrappers or expected errno semantics.

Test signals: pass/fail is reported through TST_RET, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/select/select04.c -->
