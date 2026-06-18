# File Research: sources/local-fs/apfs-fuse/ApfsLib/Decmpfs.h

This header declares the decmpfs compression interface.

`CompressionHeader` contains little-endian signature, algorithm, and uncompressed size. Public helpers classify supported algorithms and whether compressed bytes live in a resource fork.

`DecompressFile()` takes an `ApfsDir`, inode number, output vector, and compressed xattr payload. The `ApfsDir` dependency is required because some decmpfs formats store data chunks in `com.apple.ResourceFork`.

This is an APFS file-content helper, not a block-device decompressor.
