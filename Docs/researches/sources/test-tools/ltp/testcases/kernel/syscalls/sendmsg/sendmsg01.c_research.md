<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendmsg/sendmsg01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sendmsg/sendmsg01.c

Purpose: Test Name: sendmsg01 Test Description: Verify that sendmsg() returns the proper errno for various failure cases HISTORY 07/2001 Ported by Wayne Boyer 05/2003 Modified by Manoj Iyer - Make setup function set up lo device. In this shard it contributes focused coverage for sendmsg socket error and security regression coverage.

Important APIs/types/functions: uses legacy LTP API (`test.h`, `TEST`, `tst_resm`, `tst_brkm`). Key local functions: `main`, `start_server`, `do_child`, `setup`, `cleanup`, `setup0`, `cleanup0`, `setup1`, `cleanup1`, `setup2`, `setup3`, `setup4`. Key structs/tables: `test_case_t`, `tdat`. Important syscall/helper surface includes: `SAFE_CONNECT`, `SAFE_GETSOCKNAME`, `SAFE_SOCKET`, `TEST`, `TEST_LOOPING`, `TST_GET_UNUSED_PORT`, `TST_TOTAL`, `select`, `sendmsg`, `setup`, `setup0`, `setup1`, `setup2`, `setup3`, `setup4`, `setup5`, `setup6`, `setup8`, `tst_brkm`, `tst_count`, `tst_exit`, `tst_fork`, `tst_parse_opts`, `tst_require_root`.

Control flow: A legacy `main()` parses LTP options, runs setup, loops with `TEST_LOOPING`, executes cases, then calls cleanup and `tst_exit()`. table-driven cases are held in `tdat`. important local functions are `main`, `start_server`, `do_child`, `setup`, `cleanup`, `setup0`, `cleanup0`, `setup1`, `cleanup1`, `setup2`, `setup3`, `setup4`.

State and persistence behavior: exercises forked child state; temporary files or descriptors; socket endpoints or file-transfer descriptors. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; child cleanup and wait ordering matter; timing-sensitive behavior can be flaky on overloaded systems; errno expectations are kernel-version and wrapper-sensitive.

Test signals: pass/fail is reported through TEST_RETURN, TEST_ERRNO, tst_resm, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendmsg/sendmsg01.c -->
