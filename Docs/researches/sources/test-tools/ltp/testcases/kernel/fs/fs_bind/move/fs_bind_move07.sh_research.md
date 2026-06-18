# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move07.sh

Purpose: LTP `mount --move propagation` testcase for `move: private subtree to slave parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 12 expected-success command assertions, 0 expected-failure assertions, 3 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "move: private subtree to slave parent"`
- `fs_bind_makedir private dir`
- `fs_bind_makedir rshared parent2`
- `fs_bind_makedir rshared share2`
- `fs_bind_makedir rshared share1`
- `mkdir dir/grandchild`
- `EXPECT_PASS mount --bind dir share1`
- `mkdir parent2/child2`
- `EXPECT_PASS mount --bind parent2 share2`
- `EXPECT_PASS mount --make-rslave parent2`
- `EXPECT_PASS mount --move dir parent2/child2`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" parent2/child2/grandchild`
- `fs_bind_check -n parent2/child2/grandchild share2/child2/grandchild`
- `fs_bind_check -n dir/grandchild parent2/child2/grandchild`
- `fs_bind_check -n share1/grandchild parent2/child2/grandchild`
- `EXPECT_PASS umount parent2/child2/grandchild`
- `EXPECT_PASS umount parent2/child2`
- `EXPECT_PASS umount share2`
Additional operations: 4 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
