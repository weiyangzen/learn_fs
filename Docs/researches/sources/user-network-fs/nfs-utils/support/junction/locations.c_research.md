# sources/user-network-fs/nfs-utils/support/junction/locations.c

## Purpose
Provides memory-management helpers for `struct nfs_fsloc` and NUL-terminated string arrays.

## Important APIs, Types, and Functions
`nfs_free_string_array()`, `nfs_dup_string_array()`, `nfs_free_location()`, `nfs_free_locations()`, and `nfs_new_location()`.

## Control Flow
Duplication counts strings, allocates a NULL-terminated copy, and rolls back on failure. Free functions walk arrays or linked location lists and free owned fields.

## State and Persistence Behavior
Location and array ownership is heap-based and caller-managed. No persistent state.

## Dependencies and Integration Points
Used by NFS junction XML parse/build code and public libjunction callers.

## Risks and Edge Cases
Free helpers assume non-NULL location pointers where documented. Partial allocation rollback must avoid leaks.

## Test Signals
Test NULL arrays, empty arrays, multi-string duplication, allocation failure paths, single and linked location cleanup.
