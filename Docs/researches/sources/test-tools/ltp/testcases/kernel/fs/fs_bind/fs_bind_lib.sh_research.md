# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/fs_bind_lib.sh

Purpose: shared LTP shell library for the `fs_bind` mount-propagation suites. It creates a private sandbox, test disk directories, mount namespaces, bind/move/rbind helpers, propagation comparisons, and cleanup around each test case.

Important APIs/types/functions: `fs_bind_makedir`, `fs_bind_check`, `fs_bind_setup`, `_fs_bind_unmount_all`, `fs_bind_cleanup`, `_fs_bind_setup_test`, `fs_bind_create_ns`, `fs_bind_exec_ns`, `fs_bind_destroy_ns`, `_fs_bind_cleanup_test`, `fs_bind_test`, and exported LTP variables `TST_NEEDS_TMPDIR`, `TST_NEEDS_ROOT`, `TST_TESTFUNC`, `TST_SETUP`, `TST_CLEANUP`, `TST_NEEDS_CMDS`.

Control flow: library setup bind-mounts a private `sandbox`, creates four disk directories with known subtrees, and wraps the real test function named by `FS_BIND_TESTFUNC`. Each test starts from a cleaned sandbox, runs either `test` or numbered `testN`, then checks for leaked mounts and unmounts everything in reverse `/proc/mounts` order.

State/persistence behavior: creates and removes temporary directories under `TST_TMPDIR`, makes and tears down many bind mounts, and optionally creates a persistent mount namespace process id in `FS_BIND_MNTNS_PID` until cleanup kills it.

Dependencies/integration: sources `tst_test.sh` and relies on LTP `EXPECT_PASS`, `EXPECT_FAIL`, `ROD`, `tst_res`, `tst_brk`, `tst_ns_create`, and `tst_ns_exec`. Requires root plus `mount`, `umount`, `awk`, `sed`, and `diff`.

Risks/test signals: cleanup is safety-critical because leaked mounts can affect later tests. `fs_bind_check -n` treats absence/difference as expected non-propagation. Success and failure are reported through LTP `TPASS`, `TFAIL`, and `TBROK` records.
