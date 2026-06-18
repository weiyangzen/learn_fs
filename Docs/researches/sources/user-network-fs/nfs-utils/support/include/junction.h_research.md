# sources/user-network-fs/nfs-utils/support/include/junction.h

## Purpose
Public libjunction interface for managing FedFS/NFS junctions and NFS fileset location data stored on local filesystems.

## Important APIs, Types, and Functions
Defines `FedFsStatus`, `struct nfs_fsloc`, allocation/free helpers, junction CRUD/predicate APIs, cache flush, path conversion helpers, and status display helpers.

## Control Flow
Callers construct linked `nfs_fsloc` records, call `nfs_add_junction()` to serialize them into a directory xattr, query via `nfs_get_locations()`, and remove via `nfs_delete_junction()`. Status values are FedFS protocol-style rather than errno.

## State and Persistence Behavior
Location records own hostname/rootpath strings. Junctions persist as trusted xattrs and mode-bit changes on directories; helper functions allocate caller-owned structures.

## Dependencies and Integration Points
Implemented by `support/junction/*.c`, using libxml2, xattrs, and procfs cache flushing. Used by tools and export cache junction discovery.

## Risks and Edge Cases
Requires CAP_SYS_ADMIN for trusted xattrs. Struct fields mirror NFSv4 fs_locations semantics and must remain compatible with XML serialization.

## Test Signals
Test allocation/free, path conversion, add/get/delete junction round trips, status display, and permission/error mappings.
