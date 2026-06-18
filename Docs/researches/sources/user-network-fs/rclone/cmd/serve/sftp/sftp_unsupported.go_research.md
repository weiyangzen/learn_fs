<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/sftp/sftp_unsupported.go -->
# sources/user-network-fs/rclone/cmd/serve/sftp/sftp_unsupported.go

Source read: complete file, 12 lines, 319 bytes, sha256 `b68eac50482246be953190799507e0ba1faf13f3cfeb1d2bed8a7c0c9468326e`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/sftp/sftp_unsupported.go_research.md`.

## Purpose
Provides a Plan 9 stub for the SFTP serve command.

## Important APIs, types, and functions
`Command` is declared as `*cobra.Command` under the `plan9` build tag so imports can compile without a real SFTP server implementation.

## Control flow
No runtime control flow; the real command is absent on Plan 9.

## State and persistence behavior
No state.

## Dependencies and integration points
Depends only on Cobra for the symbol type.

## Risks and edge cases
Users on Plan 9 cannot use serve sftp through this implementation.

## Test signals
Build coverage is the main signal; functional SFTP tests are excluded on Plan 9.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/sftp/sftp_unsupported.go -->
