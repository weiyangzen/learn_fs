# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/cloneNS/fs_bind_cloneNS02.sh

Purpose: LTP `mount namespace propagation` testcase for `cloneNS: namespaces with parent-slave`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 11 expected-success command assertions, 0 expected-failure assertions, 9 propagation comparisons, and 3 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "cloneNS: namespaces with parent-slave"`
- `fs_bind_makedir rshared dir1`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" dir1`
- `mkdir dir2`
- `EXPECT_PASS mount --bind dir1 dir2`
- `EXPECT_PASS mount --make-slave dir2`
- `fs_bind_create_ns`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK2" dir1/a`
- `fs_bind_check dir1/a dir2/a`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK3" dir2/b`
- `fs_bind_check -n dir1/b dir2/b`
- `fs_bind_check -s "$FS_BIND_DISK2" dir1/a dir2/a`
- `fs_bind_check -s -n "$FS_BIND_DISK3" dir2/b`
- `fs_bind_check -s -n "$FS_BIND_DISK3" dir1/b`
- `fs_bind_exec_ns mount --bind "$PWD/$FS_BIND_DISK4" $PWD/dir1/c`
- `fs_bind_check -s dir1/c dir2/c`
- `fs_bind_exec_ns umount $PWD/dir2/a`
- `fs_bind_check -s -n dir1/a dir2/a`
Additional operations: 8 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
