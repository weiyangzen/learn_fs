<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/prog_rmdir.c -->
# sources/user-network-fs/libsmb2/tests/prog_rmdir.c

Purpose: Small synchronous helper that removes one SMB directory for integration tests.

Important APIs, types, and functions: Defines `usage` and `main`, using URL parse, context init, signing, `smb2_connect_share`, `smb2_rmdir`, disconnect, and cleanup.

Control flow: Connects to the share, removes the URL path, then returns status for shell scripts.

State and persistence behavior: No local persistence; remote directory removal is the persistent side effect.

Dependencies and integration points: Used by mkdir tests and ls tests for setup/cleanup.

Risks: Requires permissions and an empty target directory. Cleanup calls in scripts sometimes ignore failure, so stale test state can affect later tests.

Test signals: Covered by mkdir and ls shell tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/prog_rmdir.c -->
