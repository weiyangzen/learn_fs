<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/shell_split_test.go -->
# sources/sync-backup/restic/internal/backend/shell_split_test.go

## Purpose
Tests shell string splitting behavior for subprocess command options.

## Important APIs, Types, And Functions
TestShellSplitter and TestShellSplitterInvalid are the test entry points.

## Control Flow
Valid table cases compare parsed argument slices; invalid cases assert parser errors for malformed quoting/escaping.

## State And Persistence Behavior
No persistence.

## Dependencies And Integration Points
Depends on backend.SplitShellStrings and testing.

## Risks And Edge Cases
Coverage is parser-focused and does not execute resulting commands.

## Test Signals
Important regression signal for rclone and SFTP command option handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/shell_split_test.go -->
