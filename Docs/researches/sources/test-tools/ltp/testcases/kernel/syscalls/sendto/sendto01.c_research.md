<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendto/sendto01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sendto/sendto01.c

Purpose: Test Name: sendto01 Test Description: Verify that sendto() returns the proper errno for various failure cases HISTORY 07/2001 Ported by Wayne Boyer In this shard it contributes focused coverage for sendto socket error, SCTP, packet socket, and overflow regression coverage.

Important APIs/types/functions: uses legacy LTP API (`test.h`, `TEST`, `tst_resm`, `tst_brkm`). Key local functions: `start_server`, `do_child`, `main`, `setup`, `cleanup`, `setup0`, `cleanup0`, `setup1`, `cleanup1`, `setup2`, `setup3`. Key structs/tables: `test_case_t`, `tdat`. Important syscall/helper surface includes: `SAFE_CONNECT`, `SAFE_GETSOCKNAME`, `SAFE_SOCKET`, `TEST`, `TEST_LOOPING`, `TST_TOTAL`, `select`, `sendto`, `setup`, `setup0`, `setup1`, `setup2`, `setup3`, `tst_brkm`, `tst_count`, `tst_exit`, `tst_fork`, `tst_parse_opts`, `tst_resm`.

Control flow: A legacy `main()` parses LTP options, runs setup, loops with `TEST_LOOPING`, executes cases, then calls cleanup and `tst_exit()`. table-driven cases are held in `tdat`. important local functions are `start_server`, `do_child`, `main`, `setup`, `cleanup`, `setup0`, `cleanup0`, `setup1`, `cleanup1`, `setup2`, `setup3`.

State and persistence behavior: exercises forked child state; temporary files or descriptors; socket endpoints or file-transfer descriptors. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on standard libc/Linux syscall headers plus LTP assertion and safe-wrapper helpers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: child cleanup and wait ordering matter; timing-sensitive behavior can be flaky on overloaded systems; errno expectations are kernel-version and wrapper-sensitive.

Test signals: pass/fail is reported through TEST_RETURN, TEST_ERRNO, tst_resm, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendto/sendto01.c -->
