<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/unshare/unshare02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/unshare/unshare02.c

Purpose: Ported from Crackerjack to LTP by Manas Kumar Nayak maknayak@in.ibm.com> Basic tests for the :manpage:`unshare(2)` errors. - EINVAL on invalid flags - EPERM when process is missing required privileges

Important APIs/types/functions: includes `stdio.h`, `sys/wait.h`, `sys/types.h`, `sys/param.h`, `sys/syscall.h`, `sched.h`, `limits.h`, `unistd.h`; exercises `syscall`, `unshare`; defines `run`, `setup`; uses constants `CLONE_NEWNS`, `EINVAL`, `EPERM`.

Control flow centers on `run`, `setup`. The `struct tst_test` registration wires `.tcnt`, `.needs_tmpdir`, `.needs_root`, `.setup`, `.test` into the runner. Error-path expectations include `EINVAL`, `EPERM`.

State and persistence behavior: Runtime state is process namespaces, file descriptor tables, working directory sharing, pid namespaces, and child clone/fork synchronization.

Dependencies and integration points: Depends on namespace kernel config, root privileges for namespace creation, clone/fork helpers, and resource-limit/file-table manipulation. Direct include dependencies include `stdio.h`, `sys/wait.h`, `sys/types.h`, `sys/param.h`, `sys/syscall.h`, `sched.h`.

Risks and test signals: Namespace tests are kernel-config, privilege, and container-policy sensitive; expected TCONF is common in restricted environments. Test signals: reports through `TST_EXP_FAIL`, `TST_TEST_TCONF`; checks errno values `EINVAL`, `EPERM`; uses child/thread synchronization as part of the assertion; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/unshare/unshare02.c -->
