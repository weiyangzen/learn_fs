<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/unshare/unshare04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/unshare/unshare04.c

Purpose: This test case is to verify unshare(CLONE_NEWNS) also unshares process working directory.

Important APIs/types/functions: includes `tst_test.h`, `lapi/sched.h`; exercises `unshare`; defines `setup`, `cleanup`, `run`; uses constants `CLONE_FS`, `CLONE_NEWNS`, `SIGCHLD`.

Control flow centers on `setup`, `cleanup`, `run`. The `struct tst_test` registration wires `.needs_root`, `.needs_tmpdir`, `.test_all`, `.setup`, `.cleanup` into the runner.

State and persistence behavior: Runtime state is process namespaces, file descriptor tables, working directory sharing, pid namespaces, and child clone/fork synchronization.

Dependencies and integration points: Depends on namespace kernel config, root privileges for namespace creation, clone/fork helpers, and resource-limit/file-table manipulation. Direct include dependencies include `tst_test.h`, `lapi/sched.h`.

Risks and test signals: Namespace tests are kernel-config, privilege, and container-policy sensitive; expected TCONF is common in restricted environments. Test signals: reports through `TFAIL`, `TPASS`, `TST_EXP_PASS`; uses child/thread synchronization as part of the assertion; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/unshare/unshare04.c -->
