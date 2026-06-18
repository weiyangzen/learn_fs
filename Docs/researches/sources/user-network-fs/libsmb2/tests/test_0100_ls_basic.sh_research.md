<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0100_ls_basic.sh -->
# sources/user-network-fs/libsmb2/tests/test_0100_ls_basic.sh

Purpose: Basic shell integration test for directory listing success and failure cases.

Important APIs, types, and functions: Sources `functions.sh`; invokes `prog_ls`, `prog_mkdir`, and `prog_rmdir` against `${TESTURL}`.

Control flow: Lists the share root, ensures listing a nonexistent directory fails, creates `testdir`, verifies listing succeeds, then removes it.

State and persistence behavior: Persists a remote `testdir` briefly. No local persistent state.

Dependencies and integration points: Depends on `TESTURL`, helper binaries, and SMB server permissions.

Risks: Cleanup is best-effort; if the script aborts before rmdir, remote state can remain. Assumes `${TESTURL}/testdir` is safe to create/delete.

Test signals: Direct pass/fail shell test.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0100_ls_basic.sh -->
