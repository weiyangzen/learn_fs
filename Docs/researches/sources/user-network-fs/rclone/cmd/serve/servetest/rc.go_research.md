<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/servetest/rc.go -->
# sources/user-network-fs/rclone/cmd/serve/servetest/rc.go

Source read: complete file, 77 lines, 2005 bytes, sha256 `cefb3e4dea7b541e7475f996bbe92172010b0ad1740c6861a4e8b2ddae49d591`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/servetest/rc.go_research.md`.

## Purpose
Provides reusable tests for serve protocol rc registration and live TCP startup/shutdown.

## Important APIs, types, and functions
`GetEphemeralPort`, `checkTCP`, and `TestRc` allocate a localhost port, call rc `serve/start`, verify the returned id/address, test TCP connectivity, call `serve/stop`, and verify the port closes.

## Control flow
Protocol tests pass required rc params such as type and auth options; this helper adds `fs` and `addr`.

## State and persistence behavior
State is a temporary local directory and a live server registered in the global rc serve map until stopped.

## Dependencies and integration points
Depends on rc call registry, net dial/listen, and testify assertions.

## Risks and edge cases
There is a small race because an ephemeral port is closed then reused by the server. It assumes protocols bind TCP and support `addr` params.

## Test signals
Used by restic, sftp, webdav, and s3 tests to verify rc lifecycle behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/servetest/rc.go -->
