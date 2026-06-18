<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/sftp/handler_test.go -->
# sources/user-network-fs/rclone/cmd/serve/sftp/handler_test.go

Source read: complete file, 217 lines, 6644 bytes, sha256 `6fe40de422d9696712d48c19848525534921ec65db8d168da5f791c7ade615aa`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/sftp/handler_test.go_research.md`.

## Purpose
Tests SFTP VFS handler behavior through a real SSH/SFTP client and server.

## Important APIs, types, and functions
`startTestServer` starts a local-backed SFTP server and returns a connected `pkg/sftp.Client`. Tests cover resumed writes, truncate opens, FSETSTAT truncation, StatVFS, and Chtimes/mtime.

## Control flow
Each test writes via the SFTP client, reads back through the client, and asserts file contents, size, statfs values, or modtime.

## State and persistence behavior
State is temporary local filesystem content served through VFS cache modes selected per test.

## Dependencies and integration points
Depends on local backend, x/crypto/ssh client, pkg/sftp client, proxy defaults, VFS options, and testify.

## Risks and edge cases
Build-tagged away on Windows, Darwin, and Plan 9. Tests use insecure host-key checking and are not parallel-safe around shared constants only by convention.

## Test signals
Strong regression signal for upload resume corruption, overwrite truncation, Setstat support, and StatVFS extension behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/sftp/handler_test.go -->
