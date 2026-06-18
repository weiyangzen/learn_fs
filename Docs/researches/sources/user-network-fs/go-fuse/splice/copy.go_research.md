<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/splice/copy.go -->
# sources/user-network-fs/go-fuse/splice/copy.go

## Purpose
Provides Linux zero-copy file copying helpers built on splice pipe pairs with an `io.Copy` fallback.

## Important APIs, Types, and Functions
`SpliceCopy`, `CopyFile`, and `CopyFds` are the public functions.

## Control Flow
`SpliceCopy` repeatedly splices from source fd into a pipe, then from pipe to destination fd, stopping on EOF or short final chunk. `CopyFds` borrows a pooled pair, grows it, and falls back to `io.Copy` if unavailable.

## State and Persistence Behavior
State is borrowed from the global splice pair pool and returned after use; destination files are created/truncated by `CopyFile`.

## Dependencies and Integration Points
Depends on `Pair.LoadFrom`, `Pair.WriteTo`, `splicePool`, Linux `splice(2)`, and standard file APIs.

## Risks and Edge Cases
A short write path returns `err` even when nil, so partial splice without an error may look successful. Linux-only build tag excludes other platforms.

## Test Signals
`copy_test.go` verifies small file copy and large splice copy with max pipe growth.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/splice/copy.go -->
