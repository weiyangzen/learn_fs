# `sources/user-network-fs/go-fuse/fuse/splice_freebsd.go`

## Purpose
FreeBSD splice stub.

## Important APIs, Types, And Functions
Provides no-op splice support matching unsupported platform behavior.

## Control Flow
Provides no-op splice support matching unsupported platform behavior.

## State And Persistence
No persistent state. It prevents Linux-only zero-copy assumptions from leaking to FreeBSD.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
No persistent state. It prevents Linux-only zero-copy assumptions from leaking to FreeBSD.

## Test Signals
No persistent state. It prevents Linux-only zero-copy assumptions from leaking to FreeBSD.
