# sources/user-network-fs/samba/source3/script/tests/vfstest-acl/run.sh

Purpose: runs a scripted `vfstest` ACL scenario and fails if the scripted operations produce `NT_STATUS_ACCESS_DENIED`.

Important functions and APIs: uses `vfstest -f $TESTBASE/vfstest.cmd`, subunit, and a temporary directory under `$PREFIX`. `test_vfstest()` executes the command, checks the process status, and scans output for access denied.

Control flow: parse `VFSTEST` and `PREFIX`, create and enter a temp directory, run the one vfstest command through `testit`, then exit with the failure count.

State and persistence: creates a `vfstest_XXXXXX` temp directory under `$PREFIX` and does not remove it. The vfstest command may create files inside that temp directory.

Dependencies and integration: registered as `samba.vfstest.acl` in `nt4_dc:local` from `selftest/tests.py`. It depends on sibling `vfstest.cmd` and the `vfstest` binary.

Risks and test signals: no cleanup may accumulate temp dirs. The negative grep is broad: any `NT_STATUS_ACCESS_DENIED` in debug output fails the test, even if later expected behavior changes. Passing signal is zero exit and no access-denied status.
