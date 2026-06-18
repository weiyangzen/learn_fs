# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind37.sh

Purpose: LTP `recursive bind propagation` testcase for `rbind: private to private - with shared children`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 19 expected-success command assertions, 0 expected-failure assertions, 5 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "rbind: private to private - with shared children"`
- `mkdir parent1 parent2`
- `fs_bind_makedir rshared share1`
- `fs_bind_makedir rshared share2`
- `fs_bind_makedir rshared parent1/child1`
- `fs_bind_makedir rshared parent2/child2`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" parent1/child1`
- `EXPECT_PASS mount --rbind parent1/child1 share1`
- `EXPECT_PASS mount --rbind parent2/child2 share2`
- `EXPECT_PASS mount --rbind parent1 parent2`
- `fs_bind_check parent1 parent2`
- `fs_bind_check parent1/child1 parent2/child1`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK2" parent2/child1/a`
- `fs_bind_check parent1/child1/a parent2/child1/a share1//a`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK3" parent1/child1/b`
- `fs_bind_check parent1/child1/b parent2/child1/b share1/b`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK4" share1/c`
- `fs_bind_check parent1/child1/c parent2/child1/c share1/c`
Additional operations: 12 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
