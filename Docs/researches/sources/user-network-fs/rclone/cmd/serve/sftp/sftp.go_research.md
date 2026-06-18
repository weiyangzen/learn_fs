<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/sftp/sftp.go -->
# sources/user-network-fs/rclone/cmd/serve/sftp/sftp.go

Source read: complete file, 206 lines, 7046 bytes, sha256 `d52dc92ec47aea92e6b7583112b9a67d3673fadb9df57d273048e5ca611f8b15`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/sftp/sftp.go_research.md`.

## Purpose
Defines the `rclone serve sftp` command, SFTP options, flags, stdio mode, and rc registration for non-Plan-9 builds.

## Important APIs, types, and functions
`OptionsInfo`, `Options`, global `Opt`, `AddFlags`, and `Command` define listen address, auth credentials, authorized keys, host keys, no-auth, stdio, VFS, and proxy flags.

## Control flow
Init registers options and rc factory. Command execution either serves the remote over stdin/stdout for subsystem mode or constructs `newServer` and accepts SSH connections.

## State and persistence behavior
State is CLI/global option binding plus server runtime. Stdio mode has no listener and serves one process stream.

## Dependencies and integration points
Depends on Cobra, configstruct, VFS/proxy flag helpers, serve rc, terminal/stdin handling in `connection.go`, and `server.go`.

## Risks and edge cases
Plan 9 is excluded. Stdio mode must not run directly on a terminal. Auth-proxy mode changes required arguments because the proxy supplies the backend.

## Test signals
`sftp_test.go`, `handler_test.go`, and `servetest.TestRc` validate command/server behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/sftp/sftp.go -->
