<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setfsuid/setfsuid04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setfsuid/setfsuid04.c

Purpose: Check if setfsuid behaves correctly with file permissions. The test creates a file as ROOT with permissions 0644, does a setfsuid and then tries to open the file with RDWR permissions. The same test is done in a fork to check if new UIDs are correctly passed to the son. In this shard it contributes focused coverage for filesystem user ID transitions and permission side effects.

Important APIs/types/functions: uses legacy LTP API (`test.h`, `TEST`, `tst_resm`, `tst_brkm`). Key local functions: `main`, `do_master_child`, `setup`, `cleanup`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_OPEN`, `SETFSUID`, `TEST`, `TST_TOTAL`, `setfsuid`, `setfsuid04`, `setfsuid04_testfile`, `setup`, `tst_brkm`, `tst_count`, `tst_exit`, `tst_fork`, `tst_parse_opts`, `tst_record_childstatus`, `tst_require_root`, `tst_rmdir`, `tst_sig`, `tst_tmpdir`.

Control flow: A legacy `main()` parses LTP options, runs setup, loops with `TEST_LOOPING`, executes cases, then calls cleanup and `tst_exit()`. important local functions are `main`, `do_master_child`, `setup`, `cleanup`.

State and persistence behavior: exercises forked child state; temporary files or descriptors; process credentials. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on 16-bit UID/GID compatibility wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; child cleanup and wait ordering matter; errno expectations are kernel-version and wrapper-sensitive.

Test signals: pass/fail is reported through TEST_RETURN, TEST_ERRNO. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setfsuid/setfsuid04.c -->
