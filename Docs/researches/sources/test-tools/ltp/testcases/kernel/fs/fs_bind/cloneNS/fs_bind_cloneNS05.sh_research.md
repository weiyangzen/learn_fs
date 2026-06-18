# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/cloneNS/fs_bind_cloneNS05.sh

Purpose: LTP `mount namespace propagation` testcase for `cloneNS: namespace with multi-level chain of slaves`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 11 expected-success command assertions, 0 expected-failure assertions, 9 propagation comparisons, and 3 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "cloneNS: namespace with multi-level chain of slaves"`
- `fs_bind_makedir rshared parent`
- `fs_bind_makedir rshared parent/child1`
- `fs_bind_makedir rshared parent/child2`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK1" parent/child1`
- `EXPECT_PASS mount --rbind parent parent/child2`
- `fs_bind_create_ns`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK2" parent/child1/a`
- `fs_bind_check parent/child1/a parent/child2/child1/a`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK3" parent/child2/child1/b`
- `fs_bind_check parent/child1/b parent/child2/child1/b`
- `fs_bind_check -s "$FS_BIND_DISK2" parent/child1/a parent/child2/child1/a`
- `fs_bind_check -s "$FS_BIND_DISK3" parent/child1/b parent/child2/child1/b`
- `fs_bind_exec_ns mount --bind "$PWD/$FS_BIND_DISK4" "$PWD/parent/child2/child1/c"`
- `fs_bind_check -scheck parent/child2/child1/c parent/child1/c`
- `fs_bind_exec_ns umount "$PWD/parent/child1/b"`
- `fs_bind_check -s parent/child2/child1/b parent/child1/b`
- `fs_bind_check "$FS_BIND_DISK4" parent/child2/child1/c parent/child1/c`
Additional operations: 9 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
