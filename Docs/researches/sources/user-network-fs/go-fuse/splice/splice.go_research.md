<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/splice/splice.go -->
# sources/user-network-fs/go-fuse/splice/splice.go

## Purpose
Initializes Linux splice support, discovers pipe capacity behavior, opens `/dev/null` lazily, and wraps fcntl/pipe creation.

## Important APIs, Types, and Functions
`Resizable`, `MaxPipeSize`, `DefaultPipeSize`, `devNullFD`, `fcntl`, `osPipe`, and `newSplicePair` are the key APIs.

## Control Flow
Package init reads `/proc/sys/fs/pipe-max-size`, creates a probe pipe, checks get/set pipe size support, and records whether resizing works.

## State and Persistence Behavior
Global state includes `maxPipeSize`, `resizable`, and a lazily opened `/dev/null` fd that stays open for the process lifetime.

## Dependencies and Integration Points
Used by `Pair.Grow`, `Pair.discard`, and the pair pool. It depends on Linux `/proc`, `pipe2`, and fcntl constants.

## Risks and Edge Cases
The error check in `newSplicePair` compares `err` instead of `errNo` for `EINVAL`, so fallback may not trigger as intended. `/dev/null` fd is intentionally never closed.

## Test Signals
`TestSpliceCopy` checks pipe size sanity; unit tests should mock or assert fallback paths on kernels without resize support.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/splice/splice.go -->
