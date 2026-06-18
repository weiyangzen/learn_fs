<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0200_mkdir.sh -->
# sources/user-network-fs/libsmb2/tests/test_0200_mkdir.sh

Purpose: Basic create/remove directory integration test.

Important APIs, types, and functions: Calls `prog_mkdir` and `prog_rmdir` for `${TESTURL}/testdir` with shared `failure` handling.

Control flow: Creates a remote directory, then removes it.

State and persistence behavior: Remote `testdir` exists between the two operations.

Dependencies and integration points: Depends on writable SMB share and helper programs.

Risks: Can leave remote state if rmdir is not reached. Assumes fixed name does not collide with user data.

Test signals: Direct pass/fail mkdir/rmdir signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0200_mkdir.sh -->
