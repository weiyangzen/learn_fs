# sources/user-network-fs/rclone/backend/ftp/ftp_test.go

## Purpose
This file wires the FTP backend into rclone's generic filesystem integration test suite for several FTP server profiles.

## Important APIs, Types, And Control Flow
`TestIntegration` runs `fstests.Run` against `TestFTPRclone:`. Additional tests target ProFTPd, PureFTPd, and VsFTPd remotes and skip when the user supplied an explicit `-remote`, avoiding accidental multi-remote test runs. Each run declares `(*ftp.Object)(nil)` as the nil object type expected by the suite.

## State And Persistence
The test suite creates, reads, moves, and deletes objects on the configured FTP test remotes through `fstests`. This file itself has no persistent local state.

## Dependencies And Integration Points
It imports the production FTP package, `fstest`, and `fstests`. Server-specific remote names integrate with rclone's test configuration and the backend's internal test hook.

## Risks And Test Signals
Coverage comes from generic rclone backend behavior across four FTP implementations. It is strong for interoperability and weak for unit-level edge cases such as TLS option combinations or proxy behavior unless those remotes are configured that way.
