# sources/storage-engines/pebble/bench/util.go

## Purpose
`util.go` contains simple big-endian integer encoding helpers used to build lexicographically sortable benchmark keys.

## Important APIs, Types, And Functions
`encodeUint32Ascending` appends a uint32 in big-endian byte order. `encodeUint64Ascending` appends a uint64 in big-endian byte order.

## Control Flow
Both functions append bytes from most significant to least significant, preserving numeric ordering under bytewise comparison.

## State And Persistence Behavior
The helpers are stateless. Their output becomes part of persisted benchmark keys in queue and scan workloads.

## Dependencies And Integration Points
No external imports. Used by `queue.go`, `scan.go`, and MVCC key construction paths.

## Risks And Edge Cases
Callers must manage buffer reuse carefully because the functions append to the supplied slice. The functions intentionally do not allocate a fixed-size destination or validate capacity.

## Test Signals
No direct tests. Correctness is indirectly required by queue ordering and scan range behavior.
