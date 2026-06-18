<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utime/utime06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/utime/utime06.c

Purpose: negative coverage for `utime()` error handling: `EACCES` without write permission and `times == NULL`, `ENOENT` for a missing path, `EPERM` for explicit times by a non-owner, and `EROFS` on a read-only filesystem.

Important APIs/types/functions: `tcases[]` defines pathname, expected errno, optional `utimbuf`, and description. `setup()` creates `tmp_file`, switches to `nobody`, and the `tst_test` metadata requests a tmpdir plus read-only filesystem mount.

Control flow/state: each test case calls `utime()` once through `TST_EXP_FAIL`. State is a root-owned writable-mode file, an empty path for missing-file testing, and a read-only mount point.

Dependencies/integration: relies on LTP `needs_rofs` infrastructure and root credential setup. It does not mount the all-filesystem matrix; it targets permission and read-only behavior.

Risks/test signals: failures expose wrong errno mapping or unexpected success. The empty-string `ENOENT` case depends on Linux path handling; read-only behavior depends on the LTP rofs fixture being active.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utime/utime06.c -->
