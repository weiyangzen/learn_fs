# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move03.sh

Purpose: LTP `mount --move propagation` testcase for `move: shared subtree to slave parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 14 expected-success command assertions, 0 expected-failure assertions, 4 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "move: shared subtree to slave parent"`
- `fs_bind_makedir rshared dir`
- `fs_bind_makedir rshared parent2`
- `fs_bind_makedir rshared share1`
- `fs_bind_makedir rshared share2`
- `EXPECT_PASS mount --bind dir share1`
- `EXPECT_PASS mount --bind share2 parent2`
- `mkdir dir/grandchild`
- `mkdir parent2/child2`
- `EXPECT_PASS mount --make-rslave parent2`
- `EXPECT_PASS mount --move dir parent2/child2`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" parent2/child2/grandchild`
- `fs_bind_check parent2/child2/grandchild share1/grandchild`
- `fs_bind_check -n dir/grandchild parent2/child2/grandchild`
- `fs_bind_check -n share2/child2 parent2/child2`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK2" share1/grandchild/a`
- `fs_bind_check parent2/child2/grandchild/a share1/grandchild/a`
- `EXPECT_PASS umount share1/grandchild/a`
Additional operations: 7 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
