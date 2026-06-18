# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/cloneNS/fs_bind_cloneNS07.sh

Purpose: LTP `mount namespace propagation` testcase for `cloneNS: slave child to slave parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 9 expected-success command assertions, 0 expected-failure assertions, 11 propagation comparisons, and 2 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "cloneNS: slave child to slave parent"`
- `mkdir parent1 parent2`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" parent1`
- `EXPECT_PASS mount --make-rshared parent1`
- `EXPECT_PASS mount --bind parent1 parent2`
- `fs_bind_check parent1 parent2`
- `EXPECT_PASS mount --move parent1 parent2/a`
- `fs_bind_check parent2 parent2/a parent2/a/a`
- `fs_bind_create_ns`
- `fs_bind_check parent2 parent2/a parent2/a/a`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK2" parent2/b`
- `fs_bind_check parent2/b parent2/a/b parent2/a/a/b`
- `fs_bind_check -s parent2 parent2/a parent2/a/a`
- `fs_bind_check -s parent2/b parent2/a/b parent2/a/a/b`
- `fs_bind_exec_ns mount --bind "$PWD/$FS_BIND_DISK3" "$PWD/parent2/a/c"`
- `fs_bind_check -s parent2/c parent2/a/c parent2/a/a/c`
- `fs_bind_check parent2 parent2/a parent2/a/a`
- `fs_bind_check parent2/c parent2/a/c parent2/a/a/c`
Additional operations: 6 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
