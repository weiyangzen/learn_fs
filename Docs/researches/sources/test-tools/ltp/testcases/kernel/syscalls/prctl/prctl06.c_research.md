<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl06.c

Purpose: Test PR_GET_NO_NEW_PRIVS and PR_SET_NO_NEW_PRIVS of prctl(2). - Return the value of the no_new_privs bit for the calling thread. A value of 0 indicates the regular execve(2) behavior. A value of 1 indicates execve(2) will operate in the privilege-restricting mode. - With no_new_privs set to 1, diables privilege granting operations at execve-time. For example, a process will not be able to execute a setuid binary to change their uid or gid if this bit is set. The same is true for file capabilities. - The setting of this bit is inherited by children created by fork(2), and preserved across execve(2). We also check

Important APIs/types/functions: includes `prctl06.h`; exercises `prctl`, `fork`, `execve`; defines `do_prctl`, `verify_prctl`, `setup`; uses flags/constants `PR_GET`, `PR_GET_NO_NEW_PRIVS`, `PR_SET_NO_NEW_PRIVS`.

Control flow centers on `do_prctl`, `verify_prctl`, `setup`. The `struct tst_test` registration wires `.setup`, `.test_all`, `.forks_child`, `.needs_root`, `.mount_device`, `.mntpoint` into the LTP runner. Error-path expectations include `EINVAL`.

State and persistence behavior: Runtime state is process attributes manipulated by `prctl()`, including name strings, dumpability, death signal, timer slack, seccomp, no-new-privs, and speculation/THP controls depending on the case.

Dependencies and integration points: Depends on Linux `prctl()` option availability, LTP capability/namespace/seccomp helpers, child exec helpers, and architecture/kernel feature probes. Direct include dependencies include `prctl06.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TBROK`, `TCONF`, `TERRNO`, `TFAIL`, `TINFO`, `TPASS`, `TST_ERR`, `TST_RET`, `TTERRNO`; checks errno values `EINVAL`; uses child exit/wait status as part of the signal; runs against mounted filesystem fixtures.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl06.c -->
