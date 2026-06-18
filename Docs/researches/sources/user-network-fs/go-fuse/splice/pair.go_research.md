<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/splice/pair.go -->
# sources/user-network-fs/go-fuse/splice/pair.go

## Purpose
Defines the Linux splice pipe-pair abstraction used as an in-memory kernel pipe buffer.

## Important APIs, Types, and Functions
`Pair`, `Grow`, `MaxGrow`, `Cap`, `Close`, `Read`, `Write`, `ReadFd`, and `WriteFd` are the API.

## Control Flow
`Grow` uses `F_SETPIPE_SZ` when supported and within `maxPipeSize`; other methods wrap raw fd reads/writes and closing.

## State and Persistence Behavior
A pair owns read and write pipe fds plus its current capacity. Pool code controls reuse and final close.

## Dependencies and Integration Points
Used by copy and low-level splice functions; depends on `fcntl` constants initialized in `splice.go`.

## Risks and Edge Cases
Capacity growth can fail due to kernel limits; callers must return or close pairs exactly once to avoid leaks/double close.

## Test Signals
`TestPairSize` and `TestDiscard` exercise capacity and pipe draining; copy tests exercise read/write fd use.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/splice/pair.go -->
