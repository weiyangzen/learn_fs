<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/unshare/unshare03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/unshare/unshare03.c

Purpose: This test case based on kernel self-test unshare_test.c to check that the kernel handles the EMFILE error when a parent process changes file descriptor limits and the child process tries to unshare (CLONE_FILES).

Important APIs/types/functions: includes `tst_test.h`, `config.h`, `lapi/sched.h`; exercises `syscall`, `unshare`; defines `run`, `setup`; uses constants `CLONE_FILES`, `SIGCHLD`.

Control flow centers on `run`, `setup`. The `struct tst_test` registration wires `.needs_root`, `.test_all`, `.setup`, `.save_restore` into the runner.

State and persistence behavior: Runtime state is process namespaces, file descriptor tables, working directory sharing, pid namespaces, and child clone/fork synchronization.

Dependencies and integration points: Depends on namespace kernel config, root privileges for namespace creation, clone/fork helpers, and resource-limit/file-table manipulation. Direct include dependencies include `tst_test.h`, `config.h`, `lapi/sched.h`.

Risks and test signals: Namespace tests are kernel-config, privilege, and container-policy sensitive; expected TCONF is common in restricted environments. Test signals: reports through `TST_EXP_FAIL`, `TST_SR_TCONF`, `TST_TEST_TCONF`; uses child/thread synchronization as part of the assertion; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/unshare/unshare03.c -->
