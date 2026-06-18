# `sources/user-network-fs/go-fuse/fuse/server_unix.go`

## Purpose
Non-Linux server response writer.

## Important APIs, Types, And Functions
Defines `useSingleReader=true` and simple `Server.write` that materializes any `ReadResult` then writes header/data/payload with `writev`.

## Control Flow
Defines `useSingleReader=true` and simple `Server.write` that materializes any `ReadResult` then writes header/data/payload with `writev`.

## State And Persistence
No additional persistent state beyond request buffers. Risk is higher copy cost and correct `ReadResult.Done`/serialization on platforms without splice.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
No additional persistent state beyond request buffers. Risk is higher copy cost and correct `ReadResult.Done`/serialization on platforms without splice.

## Test Signals
No additional persistent state beyond request buffers. Risk is higher copy cost and correct `ReadResult.Done`/serialization on platforms without splice.
