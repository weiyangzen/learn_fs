<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_setaffinity/sched_setaffinity01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sched_setaffinity/sched_setaffinity01.c

Purpose: Check various errnos for sched_setaffinity(): 1. EFAULT, if the supplied memory address is invalid. 2. EINVAL, if the mask doesn't contain at least one permitted cpu. 3. ESRCH, if the process whose id is pid could not be found. 4. EPERM, if the calling process doesn't have appropriate privileges. In this shard it contributes focused coverage for CPU affinity mask setting error paths, privilege checks, and cpuset allocation.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `kill_pid`, `verify_test`, `setup`, `cleanup`. Key structs/tables: `tcase`. Important syscall/helper surface includes: `SAFE_FORK`, `SAFE_GETPWNAM`, `SAFE_KILL`, `SAFE_SETEUID`, `SAFE_WAITPID`, `TEST`, `TST_ERR`, `TST_RET`, `sched_getaffinity`, `sched_setaffinity`, `setup`, `tst_brk`, `tst_get_bad_addr`, `tst_get_unused_pid`, `tst_ncpus_max`, `tst_res`, `tst_safe_macros`, `tst_strerrno`, `tst_syscall`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `kill_pid`, `verify_test`, `setup`, `cleanup`.

State and persistence behavior: exercises forked child state; temporary files or descriptors. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on LTP syscall-number wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; child cleanup and wait ordering matter.

Test signals: pass/fail is reported through TST_RET, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sched_setaffinity/sched_setaffinity01.c -->
