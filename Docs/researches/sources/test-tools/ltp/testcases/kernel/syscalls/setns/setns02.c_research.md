<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setns/setns02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setns/setns02.c

Purpose: Copyright (c) Linux Test Project, 2014-2020 functional test for setns(2) - reassociate thread with a namespace 1. create child with CLONE_NEWUTS, set different hostname in child, set namespace back to parent ns and check that hostname has changed 2. create child with CLONE_NEWIPC, set up shared memory in parent and verify that child can't shmat it, then set namespace back to parent one and verify that child is able to do shmat In this shard it contributes focused coverage for namespace fd discovery and setns error/functional tests.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `do_child_newuts`, `do_child_newipc`, `test_flag`, `test_all`, `setup`, `cleanup`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_CLOSE`, `SAFE_GETCWD`, `SAFE_MALLOC`, `SAFE_SHMCTL`, `SAFE_SHMGET`, `SAFE_WAITPID`, `sethostname`, `setns`, `setns_dummy_uts`, `setup`, `tst_brk`, `tst_res`, `tst_safe_sysv_ipc`, `tst_syscall`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `do_child_newuts`, `do_child_newipc`, `test_flag`, `test_all`, `setup`, `cleanup`.

State and persistence behavior: exercises namespace membership. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on LTP syscall-number wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; timing-sensitive behavior can be flaky on overloaded systems.

Test signals: pass/fail is reported through tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setns/setns02.c -->
