# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind07-2.sh

Purpose: LTP `recursive bind propagation` testcase for `rbind: create slave then mount master - slave still propagates`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 10 expected-success command assertions, 0 expected-failure assertions, 2 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "rbind: create slave then mount master - slave still propagates"`
- `fs_bind_makedir rshared parent2`
- `fs_bind_makedir rshared share2`
- `EXPECT_PASS mount --rbind share2 parent2`
- `EXPECT_PASS mount --make-rslave parent2`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK1" share2`
- `fs_bind_check parent2 share2`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK2" parent2/a`
- `fs_bind_check -n parent2/a share2/a`
- `EXPECT_PASS umount parent2/a`
- `EXPECT_PASS umount parent2`
- `EXPECT_PASS umount parent2`
- `EXPECT_PASS umount parent2`
- `EXPECT_PASS umount share2`
- `EXPECT_PASS umount share2`

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
