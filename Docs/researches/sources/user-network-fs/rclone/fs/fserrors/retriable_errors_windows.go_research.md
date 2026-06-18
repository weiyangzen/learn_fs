<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fserrors/retriable_errors_windows.go -->
# sources/user-network-fs/rclone/fs/fserrors/retriable_errors_windows.go

## Purpose
Adds Windows-specific Winsock and handle/network errors to retriable classification.

## Important APIs, Types, And Control Flow
Defines selected WSA errno constants not provided uniformly by Go and appends them, along with Go syscall Windows errors, to `retriableErrors` in `init`.

## State And Persistence
Mutates the package global retry list during Windows builds.

## Dependencies And Integration Points
Selected by `windows` build tag and consumed by `ShouldRetry`.

## Risks And Test Signals
The list mirrors Windows socket error semantics and can drift as Go/syscall support changes. Coverage requires Windows test runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fserrors/retriable_errors_windows.go -->
