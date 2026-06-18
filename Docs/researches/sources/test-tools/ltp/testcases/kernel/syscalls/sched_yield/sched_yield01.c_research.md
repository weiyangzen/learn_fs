<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_yield/sched_yield01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sched_yield/sched_yield01.c

Purpose: NAME sched_yield01.C DESCRIPTION Testcase to check that sched_yield returns correct values. ALGORITHM Call sched_yield(), check its return value. If it is 0, then pass, otherwise fail with proper errno! USAGE: <for command-line> sched_yield01 [-c n] [-i n] [-I x] [-P x] [-t] where, -c n : Run n copies concurrently. -i n : Execute test n times. -I x : Execute test for x seconds. -P x : Pause for x seconds between iterations. -t : Turn on syscall timing. HISTORY 07/2001 Ported by Wayne Boyer RESTRICTIONS None In this shard it contributes focused coverage for legacy smoke coverage for sched_yield return handling.

Important APIs/types/functions: uses legacy LTP API (`test.h`, `TEST`, `tst_resm`, `tst_brkm`). Key local functions: `main`, `setup`, `cleanup`. Key structs/tables: none explicit. Important syscall/helper surface includes: `TEST`, `TEST_LOOPING`, `TST_TOTAL`, `sched_yield`, `sched_yield01`, `setup`, `tst_count`, `tst_exit`, `tst_parse_opts`, `tst_resm`, `tst_sig`.

Control flow: A legacy `main()` parses LTP options, runs setup, loops with `TEST_LOOPING`, executes cases, then calls cleanup and `tst_exit()`. important local functions are `main`, `setup`, `cleanup`.

State and persistence behavior: exercises mostly process-local syscall state with no durable repository state. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on standard libc/Linux syscall headers plus LTP assertion and safe-wrapper helpers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: errno expectations are kernel-version and wrapper-sensitive.

Test signals: pass/fail is reported through TEST_RETURN, TEST_ERRNO, tst_resm, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_yield/sched_yield01.c -->
