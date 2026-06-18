<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/splice/splice_test.go -->
# sources/user-network-fs/go-fuse/splice/splice_test.go

## Purpose
Tests Linux splice pair capacity validation and discard behavior.

## Important APIs, Types, and Functions
`TestPairSize` and `TestDiscard` are the test cases.

## Control Flow
The first grows a pair to max, writes a file bigger than capacity, and expects `LoadFrom` to reject it. The second writes data into the pipe, discards it, and expects a nonblocking read to return `EAGAIN`.

## State and Persistence Behavior
Uses global pool state and temp files; returns pairs with `Done`.

## Dependencies and Integration Points
Depends on Linux nonblocking pipe semantics and splice discard implementation.

## Risks and Edge Cases
Expected read result checks `n == -1`, which follows raw syscall conventions but may be surprising. Tests can be sensitive to pool contamination from other tests.

## Test Signals
Run with `go test ./splice`; race/fd-leak tests should include repeated pool usage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/splice/splice_test.go -->
