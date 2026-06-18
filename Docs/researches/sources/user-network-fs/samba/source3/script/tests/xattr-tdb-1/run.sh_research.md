# sources/user-network-fs/samba/source3/script/tests/xattr-tdb-1/run.sh

Purpose: runs a scripted `vfstest` scenario for the `xattr_tdb` behavior and fails on unexpected access-denied output.

Important functions and APIs: same harness pattern as the ACL vfstest runner: `vfstest -f $TESTBASE/vfstest.cmd`, subunit, and a temp working directory under `$PREFIX`.

Control flow: parse arguments, create and enter `vfstest_XXXXXX`, execute the command through `test_vfstest`, treat nonzero exit or `NT_STATUS_ACCESS_DENIED` output as failure, and exit with the failure count.

State and persistence: creates a temporary directory under `$PREFIX` and does not remove it on normal exit. Any TDB/xattr artifacts produced by `vfstest.cmd` remain in that directory.

Dependencies and integration: registered from `selftest/tests.py` as `samba.vfstest.xattr-tdb-1` in `nt4_dc:local`. Depends on sibling `vfstest.cmd`, the configured `vfstest` binary, and xattr TDB VFS behavior.

Risks and test signals: output-based access-denied detection is coarse, and lack of cleanup can accumulate artifacts. Passing signal is a clean `vfstest` exit without access-denied status text.
