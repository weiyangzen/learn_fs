<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/zipfs/zipfs.go -->
# sources/user-network-fs/go-fuse/zipfs/zipfs.go

## Purpose
Implements read-only archive filesystem dispatch and zip archive inode/file support.

## Important APIs, Types, and Functions
`zipRoot`, `NewZipTree`, `zipFile.Getattr`, `zipFile.Open`, `zipFile.Read`, and `NewArchiveFileSystem` are central.

## Control Flow
`zipRoot.OnAdd` walks zip entries, creates directory inodes, and attaches `zipFile` leaves. A `zipFile` lazily decompresses content on first open and serves reads from cached memory. Dispatch chooses zip, tar, tar.gz, or tar.bz2 by suffix.

## State and Persistence Behavior
Zip file content is cached per `zipFile` in memory after first open; the zip reader remains open for the tree lifetime.

## Dependencies and Integration Points
Depends on `archive/zip`, go-fuse node APIs, tar support in `tarfs.go`, and standard path handling.

## Risks and Edge Cases
`Read` indexes `zf.data[off:end]` with `off` as int64, so very large offsets can panic or fail to compile depending on conversion rules; negative offsets are not guarded. Zip reader close is not exposed.

## Test Signals
`zipfs_test.go` checks directory listing, file attrs, mtime, blocks, readback, and link count.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/zipfs/zipfs.go -->
