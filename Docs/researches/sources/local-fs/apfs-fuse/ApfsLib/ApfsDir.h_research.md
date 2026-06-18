# File Research: sources/local-fs/apfs-fuse/ApfsLib/ApfsDir.h

This header declares `ApfsDir`, the read-only directory/file facade over an `ApfsVolume` filesystem B-tree. Public methods cover inode metadata, directory enumeration, name lookup, file reads, xattr listing, xattr data, and xattr metadata.

Nested `Inode` stores APFS inode fields plus decoded optional xfields and a bitmask of which optional fields were present. `DirRec` stores directory entry fields including APFS hash, name, file ID, date, flags, and optional sibling ID. `XAttr` stores xattr flags, data length, and stream descriptor.

Private state caches volume reference, filesystem B-tree reference, text format flags, block size, block masks/shifts, and a temporary block buffer for partial reads.

The header declares `XAttr()` and copy constructor, but those constructors are not implemented in the corresponding `ApfsDir.cpp` file in this group, which may rely on absence of use or cause link issues if instantiated directly.
