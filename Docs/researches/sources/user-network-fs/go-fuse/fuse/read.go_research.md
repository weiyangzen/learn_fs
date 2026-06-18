# `sources/user-network-fs/go-fuse/fuse/read.go`

## Purpose
Defines `ReadResult` implementations for direct byte data and fd-backed zero-copy reads.

## Important APIs, Types, And Functions
`ReadResultData`, `ReadResultFd`, `readResultData`, `readResultFd`, `seekableResult`, and `statefulResult` are the important APIs.

## Control Flow
`ReadResultData`, `ReadResultFd`, `readResultData`, `readResultFd`, `seekableResult`, and `statefulResult` are the important APIs.

## State And Persistence
Data may be returned as in-memory bytes or lazily via `syscall.Pread`. Integration point is server response writing/splice fallback. Risks include fd lifetime, short reads at EOF, and buffer sizing.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
Data may be returned as in-memory bytes or lazily via `syscall.Pread`. Integration point is server response writing/splice fallback. Risks include fd lifetime, short reads at EOF, and buffer sizing.

## Test Signals
Data may be returned as in-memory bytes or lazily via `syscall.Pread`. Integration point is server response writing/splice fallback. Risks include fd lifetime, short reads at EOF, and buffer sizing.
