# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/fs_bind_regression.sh

Purpose: LTP `regression` testcase for `regression: bind unshared directory to unshare mountpoint | regression: rbind unshared directory to unshare mountpoint | regression: move unshared directory to unshare mountpoint`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 14 expected-success command assertions, 0 expected-failure assertions, 3 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "regression: bind unshared directory to unshare mountpoint"`
- `mkdir dir`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" dir`
- `fs_bind_check "$FS_BIND_DISK1" dir`
- `EXPECT_PASS umount dir`
- `tst_res TINFO "regression: rbind unshared directory to unshare mountpoint"`
- `mkdir dir1`
- `mkdir dir2`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" dir1`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK2" dir1/a`
- `EXPECT_PASS mount --rbind dir1 dir2`
- `fs_bind_check dir1/a dir2/a`
- `EXPECT_PASS umount dir1/a`
- `EXPECT_PASS umount dir2/a`
- `EXPECT_PASS umount dir2`
- `EXPECT_PASS umount dir1`
- `tst_res TINFO "regression: move unshared directory to unshare mountpoint"`
- `mkdir dir1`
Additional operations: 7 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
