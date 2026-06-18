# sources/test-tools/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind23.sh

Purpose: LTP `bind propagation` testcase for `bind: shared child to shared parent`. The file defines the real test function(s), then sources `fs_bind_lib.sh` for sandbox setup, LTP integration, propagation checks, and cleanup.

Important APIs/types/functions: `FS_BIND_TESTFUNC`, one or more `test` functions, `fs_bind_makedir`, `EXPECT_PASS`, `EXPECT_FAIL`, `fs_bind_check`, `tst_res TINFO`, `tst_run`, and the shared wrapper `fs_bind_test`. This file contains 10 expected-success command assertions, 0 expected-failure assertions, 2 propagation comparisons, and 0 namespace helper calls.

Control flow: the shared setup creates a private sandbox with four disk directories, then this script builds the specific mount topology and verifies expected propagation or isolation. Key operations from the source are:
- `tst_res TINFO "bind: shared child to shared parent"`
- `fs_bind_makedir private mnt`
- `fs_bind_makedir rshared mnt/1`
- `mkdir mnt/2 mnt/1/abc`
- `EXPECT_PASS mount --bind mnt/1 mnt/2`
- `EXPECT_PASS mount --bind "$FS_BIND_DISK1" mnt/1/abc`
- `fs_bind_check mnt/1/abc mnt/2/abc "$FS_BIND_DISK1"`
- `mkdir tmp2`
- `fs_bind_makedir rshared tmp1`
- `EXPECT_PASS mount --bind tmp1 tmp2`
- `mkdir tmp1/3`
- `EXPECT_PASS mount --move mnt tmp1/3`
- `fs_bind_check tmp1/3/1/abc tmp2/3/1/abc tmp2/3/2/abc "$FS_BIND_DISK1"`
- `EXPECT_PASS umount tmp1/3/1/abc`
- `EXPECT_PASS umount tmp1/3/1`
- `EXPECT_PASS umount tmp1/3/2`
- `EXPECT_PASS umount tmp1/3`
- `EXPECT_PASS umount tmp1`
Additional operations: 1 similar setup/check/cleanup lines omitted from this compact report.

State/persistence behavior: manipulates mount-table state under the temporary sandbox only. It creates transient directories and bind/rbind/move mounts, and relies on the library to unmount in reverse order and kill any namespace process.

Dependencies/integration: requires root, working Linux mount propagation semantics, `mount`, `umount`, `diff`, and LTP `tst_test.sh` helpers. Namespace variants additionally depend on `tst_ns_create` and `tst_ns_exec`.

Risks/test signals: failures indicate unexpected propagation, missing non-propagation, an incorrectly allowed unbindable clone, or cleanup leakage. `fs_bind_check` emits `TPASS`/`TFAIL`; `EXPECT_FAIL` is an intentional negative assertion for uncloneable/unbindable scenarios.
