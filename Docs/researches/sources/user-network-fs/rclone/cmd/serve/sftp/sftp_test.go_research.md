<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/sftp/sftp_test.go -->
# sources/user-network-fs/rclone/cmd/serve/sftp/sftp_test.go

Source read: complete file, 88 lines, 2182 bytes, sha256 `df25fb10c666be8debecea6c5c70e49c8003e36a4d8935e002772624ca4fcd14`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/sftp/sftp_test.go_research.md`.

## Purpose
Runs serve sftp integration tests and rc lifecycle tests.

## Important APIs, types, and functions
`TestSftp` starts an authenticated SFTP server and returns rclone SFTP backend config for generic backend tests. Interface assertions confirm `vfsHandler` satisfies pkg/sftp contracts. `TestRc` checks rc startup.

## Control flow
Tests launch the server, parse host/port from the listener, run `servetest.Run`, and cleanly shut down afterward.

## State and persistence behavior
State is temporary served remote data and a live SSH listener. Passwords are test constants and obscured in client config.

## Dependencies and integration points
Depends on local backend, servetest, obscure config, rc, VFS options, and pkg/sftp interfaces.

## Risks and edge cases
Build-tagged away on Windows, Darwin, and Plan 9. Generic backend failures can arise from client backend behavior as well as server behavior.

## Test signals
Broad signal that serve sftp can satisfy rclone's SFTP backend test suite in normal and auth-proxy local modes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/sftp/sftp_test.go -->
