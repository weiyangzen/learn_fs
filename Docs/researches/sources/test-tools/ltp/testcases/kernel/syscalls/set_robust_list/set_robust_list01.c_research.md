<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/set_robust_list/set_robust_list01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/set_robust_list/set_robust_list01.c

Purpose: Test Name: set_robust_list01 Test Description: Verify that set_robust_list() returns the proper errno for various failure cases Usage: <for command-line> set_robust_list01 [-c n] [-e][-i n] [-I x] [-p x] [-t] where, -c n : Run n copies concurrently. -e : Turn on errno logging. -i n : Execute test n times. -I x : Execute test for x seconds. -P x : Pause for x seconds between iterations. -t : Turn on syscall timing. History 07/2008 Ramon de Carvalho Valle <rcvalle@br.ibm.com> -Created Restrictions: None. In this shard it contributes focused coverage for robust futex list syscall errno validation.

Important APIs/types/functions: uses legacy LTP API (`test.h`, `TEST`, `tst_resm`, `tst_brkm`). Key local functions: `main`, `setup`, `cleanup`. Key structs/tables: `robust_list`, `robust_list_head`. Important syscall/helper surface includes: `TEST`, `TEST_LOOPING`, `TST_TOTAL`, `set_robust_list`, `set_robust_list01`, `setup`, `tst_count`, `tst_parse_opts`, `tst_resm`.

Control flow: A legacy `main()` parses LTP options, runs setup, loops with `TEST_LOOPING`, executes cases, then calls cleanup and `tst_exit()`. important local functions are `main`, `setup`, `cleanup`.

State and persistence behavior: exercises mostly process-local syscall state with no durable repository state. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on standard libc/Linux syscall headers plus LTP assertion and safe-wrapper helpers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: errno expectations are kernel-version and wrapper-sensitive.

Test signals: pass/fail is reported through TEST_RETURN, TEST_ERRNO, tst_resm, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/set_robust_list/set_robust_list01.c -->
