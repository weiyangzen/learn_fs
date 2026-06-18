<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setfsgid/setfsgid03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setfsgid/setfsgid03.c

Purpose: Testcase to check the basic functionality of setfsgid(2) system call fails when called by a non-root user. In this shard it contributes focused coverage for filesystem group ID transitions and permission side effects.

Important APIs/types/functions: uses legacy LTP API (`test.h`, `TEST`, `tst_resm`, `tst_brkm`). Key local functions: `main`, `setup`, `cleanup`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SETFSGID`, `TEST`, `TEST_LOOPING`, `TST_TOTAL`, `setfsgid`, `setfsgid03`, `setuid`, `setup`, `tst_brkm`, `tst_count`, `tst_exit`, `tst_parse_opts`, `tst_require_root`, `tst_resm`, `tst_sig`.

Control flow: A legacy `main()` parses LTP options, runs setup, loops with `TEST_LOOPING`, executes cases, then calls cleanup and `tst_exit()`. important local functions are `main`, `setup`, `cleanup`.

State and persistence behavior: exercises process credentials. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on 16-bit UID/GID compatibility wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; credential mutations must stay isolated to child processes or be restored.

Test signals: pass/fail is reported through TEST_RETURN, tst_resm, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setfsgid/setfsgid03.c -->
