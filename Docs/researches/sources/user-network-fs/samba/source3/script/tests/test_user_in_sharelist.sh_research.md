# sources/user-network-fs/samba/source3/script/tests/test_user_in_sharelist.sh

Purpose: validates that a user-specific `[homes]` share appears in `srvsvc` share enumeration output. It is a focused regression test for homes share visibility through `rpcclient netshareenum`.

Important functions and APIs: the script uses `rpcclient`, selftest-provided `USER` and `PASSWORD`, and `subunit.sh`. It runs `rpcclient SERVER -UUSER%PASSWORD -c netshareenum` and searches for a `netname: USER$` line.

Control flow: after argument validation, it invokes the single RPC enumeration command, captures `grep` status, reports the result through `testit`, and finishes with `testok`.

State and persistence: no local persistent state is created. It only reads server share enumeration state exposed by the test environment.

Dependencies and integration: registered in `selftest/tests.py` as `samba3.blackbox.netshareenum_username` against the `fileserver` environment. It assumes homes support is configured so that the authenticating user maps to a visible share named with a trailing dollar.

Risks and test signals: the check is intentionally narrow and can fail from output formatting changes, environment user naming changes, or homes share configuration drift. Passing signal is the exact `netname` line in RPC output.
