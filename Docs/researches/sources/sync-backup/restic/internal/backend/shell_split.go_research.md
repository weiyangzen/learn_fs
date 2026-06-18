<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/shell_split.go -->
# sources/sync-backup/restic/internal/backend/shell_split.go

## Purpose
Implements shell-like command string splitting for backend subprocess options.

## Important APIs, Types, And Functions
SplitShellStrings and its internal scanner/state logic are the API.

## Control Flow
The parser scans runes, handles whitespace separation, quotes, backslash escapes, and error cases for unterminated quotes or invalid escapes.

## State And Persistence Behavior
No persistent state; parsing state is local to a call.

## Dependencies And Integration Points
Depends on strings/unicode-style parsing and internal/errors.

## Risks And Edge Cases
Shell compatibility is intentionally limited; mismatches can affect sftp.command, sftp.args, rclone.program, and rclone.args.

## Test Signals
shell_split_test.go covers valid and invalid parsing cases.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/shell_split.go -->
