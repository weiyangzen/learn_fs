<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0210_cp_basic.sh -->
# sources/user-network-fs/libsmb2/tests/test_0210_cp_basic.sh

Purpose: Basic copy integration test covering local-to-SMB and SMB-to-local directions.

Important APIs, types, and functions: Uses `../utils/smb2-cp`, `cmp`, local files `testfile`/`testfile2`, and `${TESTURL}/testfile`.

Control flow: Creates a local file, copies it to the share, copies it back, compares contents, then verifies copying a nonexistent SMB file fails.

State and persistence behavior: Persists local temporary files and a remote test file unless cleaned externally; script removes `testfile2` at start only.

Dependencies and integration points: Depends on `smb2-cp`, writable SMB share, and standard `cmp`.

Risks: Remote `testfile` may be overwritten and is not removed here. Fixed names can collide with existing data.

Test signals: Direct copy correctness and negative-path signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0210_cp_basic.sh -->
