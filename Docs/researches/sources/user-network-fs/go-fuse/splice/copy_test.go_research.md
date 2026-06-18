<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/splice/copy_test.go -->
# sources/user-network-fs/go-fuse/splice/copy_test.go

## Purpose
Tests Linux splice copy helpers.

## Important APIs, Types, and Functions
`TestCopyFile` and `TestSpliceCopy` cover file-level and pair-level copying.

## Control Flow
Tests create temp files, write known data, call the copy helpers, and inspect destination contents or pipe sizing.

## State and Persistence Behavior
State is temp files and a temporary splice pair that is closed manually in the large-copy test.

## Dependencies and Integration Points
Depends on the Linux splice package and `/proc/sys/fs/pipe-max-size` indirectly.

## Risks and Edge Cases
The large-copy test does not validate destination bytes after `SpliceCopy`, so it mainly catches setup and syscall failures.

## Test Signals
Run with `go test ./splice` on Linux; additional assertions should compare the 2 MiB destination content.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/splice/copy_test.go -->
