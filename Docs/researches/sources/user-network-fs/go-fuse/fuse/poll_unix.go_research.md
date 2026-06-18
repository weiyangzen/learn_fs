# `sources/user-network-fs/go-fuse/fuse/poll_unix.go`

## Purpose
Non-Darwin poll-hack implementation using `golang.org/x/sys/unix.Poll`.

## Important APIs, Types, And Functions
`pollHack` opens `.go-fuse-epoll-hack`, polls for read/priority/write events with timeout 0, and closes the fd.

## Control Flow
`pollHack` opens `.go-fuse-epoll-hack`, polls for read/priority/write events with timeout 0, and closes the fd.

## State And Persistence
No persistent state. Dependencies are `syscall` and `unix`. Risk is failure to open the mountpoint during startup; `WaitMount` propagates errors.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
No persistent state. Dependencies are `syscall` and `unix`. Risk is failure to open the mountpoint during startup; `WaitMount` propagates errors.

## Test Signals
No persistent state. Dependencies are `syscall` and `unix`. Risk is failure to open the mountpoint during startup; `WaitMount` propagates errors.
