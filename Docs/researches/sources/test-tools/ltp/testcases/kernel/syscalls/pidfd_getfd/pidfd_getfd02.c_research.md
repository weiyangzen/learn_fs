<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_getfd/pidfd_getfd02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_getfd/pidfd_getfd02.c

Purpose: Tests basic error handling of the pidfd_open syscall. - EBADF pidfd is not a valid PID file descriptor - EBADF targetfd is not an open file descriptor in the process referred to by pidfd - EINVAL flags is not 0 - ESRCH the process referred to by pidfd does not exist (it has terminated and been waited on) - EPERM the calling process doesn't have PTRACE_MODE_ATTACH_REALCREDS permissions over the process referred to by pidfd

Important APIs/types/functions: includes `stdlib.h`, `pwd.h`, `tst_test.h`, `tst_safe_macros.h`, `lapi/pidfd.h`; exercises `pidfd_getfd`, `pidfd_open`; defines `setup`, `cleanup`, `run`; uses flags/constants `PTRACE_MODE_ATTACH_REALCREDS`.

Control flow centers on `setup`, `cleanup`, `run`. The `struct tst_test` registration wires `.tcnt`, `.test`, `.setup`, `.cleanup`, `.needs_root`, `.forks_child` into the LTP runner. Named case hints include `invalid pidfd`, `invalid targetfd`, `invalid flags`, `the process referred to by pidfd doesn't exist`, `lack of required permission`. Error-path expectations include `EBADF`, `EINVAL`, `EPERM`, `ESRCH`.

State and persistence behavior: Runtime state is pidfd references to child processes plus source and duplicated file descriptors guarded by ptrace-style permission checks.

Dependencies and integration points: Depends on pidfd and pidfd_getfd syscall wrappers, forked children, file descriptor passing expectations, and ptrace-like permission policy. Direct include dependencies include `stdlib.h`, `pwd.h`, `tst_test.h`, `tst_safe_macros.h`, `lapi/pidfd.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TST_CHECKPOINT_WAIT`, `TST_CHECKPOINT_WAKE`, `TST_EXP_FAIL2`; checks errno values `EBADF`, `EINVAL`, `EPERM`, `ESRCH`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_getfd/pidfd_getfd02.c -->
