<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/sftp/connection_test.go -->
# sources/user-network-fs/rclone/cmd/serve/sftp/connection_test.go

Source read: complete file, 25 lines, 504 bytes, sha256 `b1db60ba63bddbc300badd8410d915ba0e853b6437dde13f7aaa382a3f4939e5`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/sftp/connection_test.go_research.md`.

## Purpose
Tests SFTP shell-unescape behavior used for exec command arguments.

## Important APIs, types, and functions
`TestShellEscape` verifies escaping and newline restoration for strings that were shell-escaped by rclone.

## Control flow
The test calls `shellUnEscape` directly with table cases.

## State and persistence behavior
No state.

## Dependencies and integration points
Depends on the regex and string replacement behavior in `connection.go`.

## Risks and edge cases
It covers only argument unescaping, not full exec command parsing.

## Test signals
Regression signal for hashsum paths containing escaped characters or embedded newlines.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/sftp/connection_test.go -->
