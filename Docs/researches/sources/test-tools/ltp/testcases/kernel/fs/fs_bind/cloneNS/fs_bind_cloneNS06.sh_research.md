# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/cloneNS/fs_bind_cloneNS06.sh

Purpose: LTP `mount namespace propagation` testcase for `cloneNS: namespace with shared point bind mounted within the same directory`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 19 expected-success command assertions, 0 expected-failure assertions, 18 propagation comparisons, and 3 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "cloneNS: namespace with shared point bind mounted within the same directory"`
- `fs_bind_makedir rshared dir1`
- `mkdir dir1/x dir2 dir3 dir4`
- `EXPECT_PASS mount --rbind dir1 dir2`
- `EXPECT_PASS mount --make-rslave dir2`
- `EXPECT_PASS mount --make-rshared dir2`
- `EXPECT_PASS mount --rbind dir2 dir3`
- `EXPECT_PASS mount --make-rslave dir3`
- `EXPECT_PASS mount --make-rshared dir3`
- `EXPECT_PASS mount --rbind dir3 dir4`
- `EXPECT_PASS mount --make-rslave dir4`
- `fs_bind_create_ns`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK1" dir1/x`
- `fs_bind_check dir1/x dir2/x dir3/x dir4/x`
- `EXPECT_PASS mount --rbind "$FS_BIND_DISK2" dir2/x/a`
- `fs_bind_check -n dir1/x/a dir2/x/a`
- `fs_bind_check dir2/x/a dir3/x/a dir4/x/a`
- `fs_bind_check -s dir1/x dir2/x dir3/x dir4/x`
Additional operations: 25 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
