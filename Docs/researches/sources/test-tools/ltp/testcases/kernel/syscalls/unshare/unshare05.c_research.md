<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/unshare/unshare05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/unshare/unshare05.c

Purpose: This test case verifies unshare(CLONE_NEWPID) creates a new PID namespace and that the first child process in the new namespace gets PID 1.

Important APIs/types/functions: includes `tst_test.h`, `lapi/sched.h`; exercises `unshare`; defines `setup`, `run`; uses constants `CLONE_NEWPID`, `SIGCHLD`.

Control flow centers on `setup`, `run`. The `struct tst_test` registration wires `.setup`, `.needs_root`, `.test_all`, `.needs_kconfigs` into the runner. Named case hints include `CONFIG_PID_NS`.

State and persistence behavior: Runtime state is process namespaces, file descriptor tables, working directory sharing, pid namespaces, and child clone/fork synchronization.

Dependencies and integration points: Depends on namespace kernel config, root privileges for namespace creation, clone/fork helpers, and resource-limit/file-table manipulation. Direct include dependencies include `tst_test.h`, `lapi/sched.h`.

Risks and test signals: Namespace tests are kernel-config, privilege, and container-policy sensitive; expected TCONF is common in restricted environments. Test signals: reports through `TST_EXP_EQ_LI`; uses child/thread synchronization as part of the assertion; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/unshare/unshare05.c -->
