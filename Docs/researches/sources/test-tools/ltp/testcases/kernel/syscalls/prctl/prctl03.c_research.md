<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl03.c

Purpose: Test PR_SET_CHILD_SUBREAPER and PR_GET_CHILD_SUBREAPER of prctl(2). - If PR_SET_CHILD_SUBREAPER marks a process as a child subreaper, it fulfills the role of init(1) for its descendant orphaned process. The PPID of its orphaned process will be reparented to the subreaper process, and the subreaper process can receive a SIGCHLD signal and wait(2) on the orphaned process to discover corresponding termination status. - The setting of PR_SET_CHILD_SUBREAPER is not inherited by children reated by fork(2). - PR_GET_CHILD_SUBREAPER can get the setting of PR_SET_CHILD_SUBREAPER. These flags was added by kernel commit ebe

Important APIs/types/functions: includes `errno.h`, `stdlib.h`, `unistd.h`, `sys/types.h`, `sys/wait.h`, `signal.h`, `sys/prctl.h`, `tst_test.h`; exercises `prctl`, `fork`; defines `check_get_subreaper`, `verify_prctl`, `sighandler`, `setup`; uses flags/constants `PR_GET_CHILD_SUBREAPER`, `PR_SET_CHILD_SUBREAPER`.

Control flow centers on `check_get_subreaper`, `verify_prctl`, `sighandler`, `setup`. The `struct tst_test` registration wires `.setup`, `.forks_child`, `.test_all` into the LTP runner. Error-path expectations include `EINVAL`.

State and persistence behavior: Runtime state is process attributes manipulated by `prctl()`, including name strings, dumpability, death signal, timer slack, seccomp, no-new-privs, and speculation/THP controls depending on the case.

Dependencies and integration points: Depends on Linux `prctl()` option availability, LTP capability/namespace/seccomp helpers, child exec helpers, and architecture/kernel feature probes. Direct include dependencies include `errno.h`, `stdlib.h`, `unistd.h`, `sys/types.h`, `sys/wait.h`, `signal.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TCONF`, `TERRNO`, `TFAIL`, `TPASS`, `TST_CHECKPOINT_WAIT`, `TST_CHECKPOINT_WAKE`, `TST_ERR`, `TST_RET`, `TTERRNO`; checks errno values `EINVAL`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl03.c -->
