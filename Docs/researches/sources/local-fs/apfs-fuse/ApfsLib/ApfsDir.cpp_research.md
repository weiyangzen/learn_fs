# File Research: sources/local-fs/apfs-fuse/ApfsLib/ApfsDir.cpp

`ApfsDir` implements APFS filesystem-tree operations: inode lookup, directory listing, name lookup, file content reads, extended attribute listing, extended attribute retrieval, xattr info retrieval, and key comparators for normal filesystem and sealed-volume extent trees.

`GetInode()` looks up `APFS_TYPE_INODE` keys and copies core inode fields plus optional xfields such as snapshot XID, delta tree OID, document ID, name, previous file size, dstream, FS UUID, and sparse-byte count.

`ListDirectory()` iterates `APFS_TYPE_DIR_REC` entries under a parent inode. It supports both legacy and hashed directory record keys depending on volume text format flags, and decodes sibling-id xfields. `LookupName()` builds the exact key, including APFS filename hash for case/normalization-insensitive volumes.

`ReadFile()` resolves file extents and reads file data through `ApfsVolume::ReadBlocks()`. For sealed volumes it uses the fext tree; otherwise it uses regular filesystem-tree file extent records. Sparse extents are zero-filled.

Xattr paths support embedded xattrs and stream-backed xattrs; stream-backed data is read through `ReadFile()` using the xattr object ID and dstream sizes.

Notable risks: many xfield size checks are `assert()`, so release builds may continue on malformed data. Several TODOs remain for Finder info, dir stats, and sealed-volume crypto handling.
