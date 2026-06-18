<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/restic/stdio_conn.go -->
# sources/user-network-fs/rclone/cmd/serve/restic/stdio_conn.go

Source read: complete file, 73 lines, 1396 bytes, sha256 `8a6e171648b2bc527949b2c740ba405562191e26d26451a8887a1e45ccb4b89c`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/restic/stdio_conn.go_research.md`.

## Purpose
Adapts stdin/stdout files to `net.Conn` so restic can start rclone and communicate over HTTP/2 on standard streams.

## Important APIs, types, and functions
`Addr` implements `net.Addr`; `StdioConn` implements `Read`, `Write`, `Close`, address accessors, and deadline methods.

## Control flow
Restic command startup constructs `StdioConn` and passes it to `http2.Server.ServeConn` when `--stdio` is enabled.

## State and persistence behavior
State is the two process file descriptors. `Close` closes stdin and stdout; deadlines are delegated to the files.

## Dependencies and integration points
Depends on `os.File`, `net.Conn`, and `time` deadline APIs.

## Risks and edge cases
Deadline support depends on the underlying file descriptors. Running on a terminal is rejected in `restic.go`, not here.

## Test signals
Exercised indirectly by stdio mode users; no direct unit test in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/restic/stdio_conn.go -->
