<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_getfd/pidfd_getfd01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_getfd/pidfd_getfd01.c

Purpose: Basic pidfd_getfd() test: - the close-on-exec flag is set on the file descriptor returned by pidfd_getfd - use kcmp to check whether a file descriptor idx1 in the process pid1 refers to the same open file description as file descriptor idx2 in the process pid2

Important APIs/types/functions: includes `unistd.h`, `stdlib.h`, `stdio.h`, `tst_test.h`, `lapi/kcmp.h`, `tst_safe_macros.h`, `lapi/pidfd.h`; exercises `pidfd_getfd`; defines `do_child`, `run`, `setup`, `cleanup`.

Control flow centers on `do_child`, `run`, `setup`, `cleanup`. The `struct tst_test` registration wires `.needs_root`, `.forks_child`, `.setup`, `.cleanup`, `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is pidfd references to child processes plus source and duplicated file descriptors guarded by ptrace-style permission checks.

Dependencies and integration points: Depends on pidfd and pidfd_getfd syscall wrappers, forked children, file descriptor passing expectations, and ptrace-like permission policy. Direct include dependencies include `unistd.h`, `stdlib.h`, `stdio.h`, `tst_test.h`, `lapi/kcmp.h`, `tst_safe_macros.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_CHECKPOINT_WAIT`, `TST_CHECKPOINT_WAKE`, `TST_EXP_FD_SILENT`, `TST_EXP_VAL_SILENT`, `TST_PROCESS_STATE_WAIT`, `TST_RET`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_getfd/pidfd_getfd01.c -->
