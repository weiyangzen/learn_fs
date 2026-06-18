# `sources/user-network-fs/go-fuse/fuse/poll.go`

## Purpose
Implements the Go runtime epoll avoidance hack for FUSE `_OP_POLL`.

## Important APIs, Types, And Functions
Defines `pollHackName`, `pollHackInode`, and `doPollHackLookup` handling LOOKUP/OPEN/GETATTR/SETATTR/GETXATTR/POLL/ACCESS/FLUSH/RELEASE for the synthetic file.

## Control Flow
Defines `pollHackName`, `pollHackInode`, and `doPollHackLookup` handling LOOKUP/OPEN/GETATTR/SETATTR/GETXATTR/POLL/ACCESS/FLUSH/RELEASE for the synthetic file.

## State And Persistence
No persisted state; it synthesizes a fake inode and returns ENOSYS for POLL so the kernel stops polling. Integrated from `protocolServer.handleRequest` and `Server.WaitMount`. Risk is accidentally disabling unrelated kernel features with ENOSYS, so unsupported opcodes return ERANGE.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
No persisted state; it synthesizes a fake inode and returns ENOSYS for POLL so the kernel stops polling. Integrated from `protocolServer.handleRequest` and `Server.WaitMount`. Risk is accidentally disabling unrelated kernel features with ENOSYS, so unsupported opcodes return ERANGE.

## Test Signals
No persisted state; it synthesizes a fake inode and returns ENOSYS for POLL so the kernel stops polling. Integrated from `protocolServer.handleRequest` and `Server.WaitMount`. Risk is accidentally disabling unrelated kernel features with ENOSYS, so unsupported opcodes return ERANGE.
