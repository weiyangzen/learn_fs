<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/set_mempolicy/set_mempolicy01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/set_mempolicy/set_mempolicy01.c

Purpose: In most cases, set_mempolicy01 finish quickly, but when the platform has multiple NUMA nodes, the test matrix combination grows exponentially and bring about test time to increase extremely fast. Here reset the entire timeout according to the NUMA nodes. In this shard it contributes focused coverage for NUMA memory policy behavior and architecture-specific compat syscall regression coverage.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `cleanup`, `verify_mempolicy`, `verify_set_mempolicy`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_FORK`, `TEST`, `TST_NUMA_MEM`, `TST_RET`, `TST_TEST_TCONF`, `numa_allocate_nodemask`, `numa_bitmask_setbit`, `numa_free_nodemask`, `set_mempolicy`, `set_mempolicy01`, `setup`, `tse_get_nodemap`, `tse_mempolicy_mode_name`, `tse_nodemap`, `tse_nodemap_free`, `tse_nodemap_print_counters`, `tse_nodemap_reset_counters`, `tse_numa`, `tst_brk`, `tst_reap_children`, `tst_res`, `tst_set_timeout`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setup`, `cleanup`, `verify_mempolicy`, `verify_set_mempolicy`.

State and persistence behavior: exercises forked child state; NUMA policy and page placement. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on NUMA/libnuma and `tse_numa` helpers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: child cleanup and wait ordering matter.

Test signals: pass/fail is reported through TST_RET, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/set_mempolicy/set_mempolicy01.c -->
