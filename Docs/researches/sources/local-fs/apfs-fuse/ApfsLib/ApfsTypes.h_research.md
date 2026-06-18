# File Research: sources/local-fs/apfs-fuse/ApfsLib/ApfsTypes.h

This small header defines common APFS scalar aliases used across the library.

Types are `apfs_uuid_t` as a 16-byte array, `paddr_t` as `uint64_t`, `oid_t` as `uint64_t`, and `xid_t` as `uint64_t`.

The comment notes Apple treats physical addresses as signed in some contexts, but this implementation uses unsigned `uint64_t`.

It is a low-level dependency for mappers, disk structs, and APFS parsing code.
