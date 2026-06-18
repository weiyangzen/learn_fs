<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/prog_mkdir.c -->
# sources/user-network-fs/libsmb2/tests/prog_mkdir.c

Purpose: Small synchronous helper that creates one SMB directory for integration tests.

Important APIs, types, and functions: Defines `usage` and `main`, using URL parse, context init, signing, `smb2_connect_share`, `smb2_mkdir`, disconnect, URL/context cleanup.

Control flow: The command connects to the share identified by the URL, calls mkdir on the URL path, and exits nonzero on setup or operation failure.

State and persistence behavior: No persistent local state; remote directory creation is the intended persistent side effect until paired with rmdir.

Dependencies and integration points: Used by mkdir tests and setup/cleanup in ls tests.

Risks: Requires a writable SMB share. If cleanup tests fail later, remote test directories can remain.

Test signals: Covered by `test_0200_mkdir.sh`, `test_0201_mkdir_valgrind.sh`, and ls setup flows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/prog_mkdir.c -->
