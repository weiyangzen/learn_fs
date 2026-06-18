<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/zipfs/tarfs.go -->
# sources/user-network-fs/go-fuse/zipfs/tarfs.go

## Purpose
Builds a read-only go-fuse inode tree from tar, tar.gz, or tar.bz2 archives.

## Important APIs, Types, and Functions
`HeaderToFileInfo`, `tarRoot.OnAdd`, `readCloser`, and `NewTarCompressedTree` are key APIs.

## Control Flow
On add, it streams tar entries, handles GNU long-name records, reads each file body, creates missing directory inodes, maps tar metadata into `fuse.Attr`, and installs memory files, symlinks, directories, device-like nodes, or FIFOs.

## State and Persistence Behavior
All archive content is loaded into memory inode/file objects during `OnAdd`; compressed input file handles are closed after reading.

## Dependencies and Integration Points
Depends on `archive/tar`, gzip, bzip2, go-fuse memory inode types, and archive dispatch in `zipfs.go`.

## Risks and Edge Cases
Large archives can consume large memory; hard links are logged but unsupported; directory entries are represented with `MemRegularFile` plus directory mode, which is unusual but works for attrs.

## Test Signals
`tarfs_test.go` covers directories, regular files, attributes, and readback; symlink test data is present conditionally.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/zipfs/tarfs.go -->
