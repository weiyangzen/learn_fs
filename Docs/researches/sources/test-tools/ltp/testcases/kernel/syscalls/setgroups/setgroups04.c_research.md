<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setgroups/setgroups04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setgroups/setgroups04.c

Purpose: Test Name: setgroups04 Test Description: Verify that, setgroups() fails with -1 and sets errno to EFAULT if the list has an invalid address. Expected Result: setgroups() should fail with return value -1 and set expected errno. Algorithm: Setup: Setup signal handling. Pause for SIGUSR1 if option specified. Test: Loop if the proper options are given. Execute system call Check return code, if system call failed (return=-1) if errno set == expected errno Issue sys call fails with expected return value and errno. Otherwise, Issue sys call fails with unexpected errno. Otherwise, Issue sys call returns unexpected value. In this shard it contributes focused coverage for supplementary group list setting, bounds, privilege, and bad-pointer validation.

Important APIs/types/functions: uses legacy LTP API (`test.h`, `TEST`, `tst_resm`, `tst_brkm`). Key local functions: `main`, `setup`, `cleanup`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SETGROUPS`, `TEST`, `TEST_LOOPING`, `TST_TOTAL`, `setgroups`, `setgroups04`, `sets`, `setup`, `tst_count`, `tst_exit`, `tst_parse_opts`, `tst_require_root`, `tst_resm`, `tst_sig`.

Control flow: A legacy `main()` parses LTP options, runs setup, loops with `TEST_LOOPING`, executes cases, then calls cleanup and `tst_exit()`. important local functions are `main`, `setup`, `cleanup`.

State and persistence behavior: exercises process credentials. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on 16-bit UID/GID compatibility wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; errno expectations are kernel-version and wrapper-sensitive.

Test signals: pass/fail is reported through TEST_RETURN, TEST_ERRNO, tst_resm, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setgroups/setgroups04.c -->
