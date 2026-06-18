<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/seccomp/seccomp01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/seccomp/seccomp01.c

Purpose: Test PR_GET_SECCOMP and PR_SET_SECCOMP with both prctl(2) and seccomp(2). The second one is called via __NR_seccomp using tst_syscall(). - If PR_SET_SECCOMP sets the SECCOMP_MODE_STRICT for the calling thread, the only system call that the thread is permitted to make are read(2), write(2),_exit(2)(but not exit_group(2)), and sigreturn(2). Other system calls result in the delivery of a SIGKILL signal. This operation is available only if the kernel is configured with CONFIG_SECCOMP enabled. - If PR_SET_SECCOMP sets the SECCOMP_MODE_FILTER for the calling thread, the system calls allowed are defined by a pointer to a Berkeley Packet Filter. Other system calls result int the delivery of a SIGSYS signal with SECCOMP_RET_KILL. In this shard it contributes focused coverage for seccomp strict/filter mode behavior through prctl and seccomp syscalls.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `check_filter_mode_inherit`, `check_strict_mode`, `check_filter_mode`, `verify_prctl`, `setup`. Key structs/tables: `tcase`, `strict_filter`. Important syscall/helper surface includes: `GET_SECCOMP`, `SAFE_FORK`, `SAFE_OPEN`, `SAFE_READ`, `SAFE_WAITPID`, `SAFE_WRITE`, `SAFE_WRITE_ALL`, `TEST`, `TST_RET`, `prctl`, `seccomp`, `sets`, `setup`, `tst_brk`, `tst_kconfig`, `tst_kconfig_check`, `tst_res`, `tst_syscall`, `tst_test`, `tst_variant`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. table-driven cases are held in `strict_filter`. important local functions are `check_filter_mode_inherit`, `check_strict_mode`, `check_filter_mode`, `verify_prctl`, `setup`.

State and persistence behavior: exercises forked child state; temporary files or descriptors; thread seccomp mode. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on LTP syscall-number wrappers, root privileges, kernel config gating. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; child cleanup and wait ordering matter.

Test signals: pass/fail is reported through TST_RET, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/seccomp/seccomp01.c -->
