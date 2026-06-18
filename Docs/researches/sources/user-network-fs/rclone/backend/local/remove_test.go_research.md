
# sources/user-network-fs/rclone/backend/local/remove_test.go

## Purpose
Tests local `remove` behavior when the file is still open.

## Important APIs, Types, And Control Flow
`TestRemove` creates a temp file, checks it exists, schedules background close after 250 ms using a wait group, calls `remove`, asserts no error and non-existence, then waits for close completion.

## State And Persistence
Creates and deletes one temporary file outside the repository.

## Dependencies And Integration Points
Exercised against platform-specific `remove` implementations. On Windows it validates sharing-violation retry; on Unix it validates ordinary unlink semantics.

## Risks And Test Signals
Timing-dependent on Windows retry behavior but bounded. It catches regressions in deletion retry and temp-file cleanup.
