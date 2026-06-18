<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendmsg/sendmsg03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sendmsg/sendmsg03.c

Purpose: CVE-2017-17712 Test for race condition vulnerability in sendmsg() on SOCK_RAW sockets. Changing the value of IP_HDRINCL socket option in parallel with sendmsg() call may lead to uninitialized stack pointer usage, allowing arbitrary code execution or privilege escalation. Fixed in 4.15 8f659a03a0ba ("net: ipv4: fix for a race condition in raw_sendmsg") In this shard it contributes focused coverage for sendmsg socket error and security regression coverage.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `cleanup`, `run`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_CLOSE`, `SAFE_SETSOCKOPT_INT`, `SAFE_SOCKET`, `TST_SR_SKIP`, `TST_TAINT_D`, `TST_TAINT_W`, `sendmsg`, `setsockopt`, `setup`, `tst_fuzzy_sync`, `tst_fzsync_end_race_a`, `tst_fzsync_end_race_b`, `tst_fzsync_pair`, `tst_fzsync_pair_cleanup`, `tst_fzsync_pair_init`, `tst_fzsync_pair_reset`, `tst_fzsync_run_a`, `tst_fzsync_run_b`, `tst_fzsync_start_race_a`, `tst_fzsync_start_race_b`, `tst_path_val`, `tst_res`, `tst_setup_netns`, `tst_tag`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setup`, `cleanup`, `run`.

State and persistence behavior: exercises socket endpoints or file-transfer descriptors. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on kernel config gating. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: timing-sensitive behavior can be flaky on overloaded systems; regression tags tie behavior to specific kernel fixes.

Test signals: pass/fail is reported through tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendmsg/sendmsg03.c -->
