<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/zipfs/multizip_test.go -->
# sources/user-network-fs/go-fuse/zipfs/multizip_test.go

## Purpose
Tests dynamic multi-archive mounting through the `MultiZipFs` config symlink interface.

## Important APIs, Types, and Functions
`setupMzfs`, `TestMultiZipReadonly`, and `TestMultiZipFs` are the main tests.

## Control Flow
Tests mount `MultiZipFs`, verify root/config write restrictions, symlink a test zip into `/config/zipmount`, inspect `/zipmount`, read the config symlink target, and unlink it to ensure the mounted tree disappears or is unreachable.

## State and Persistence Behavior
State is a temp FUSE mount and the test zip file; cleanup unmounts the server.

## Dependencies and Integration Points
Depends on FUSE support, `testZipFile`, and kernel notify support for strict invalidation checks.

## Risks and Edge Cases
If invalid inode notifications are unsupported, the removal assertion falls back to directory listing, so stale path behavior is less strictly tested.

## Test Signals
Running `go test ./zipfs` covers these flows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/zipfs/multizip_test.go -->
