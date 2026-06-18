# sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_debug.h

## Purpose

This header exposes a debug-only helper for white-box tests or diagnostics that need the sub-FSAL object handle under an MDCACHE object. It explicitly warns against production use. The source was read as a complete 59-line file.

## Important APIs, Types, and Functions

It defines `mdcdb_get_sub_handle(struct fsal_obj_handle *obj_hdl)`, which uses `container_of` to convert the MDCACHE object handle to `mdcache_entry_t` and returns `entry->sub_handle`.

## Control Flow

The helper performs a direct field lookup with no locking, no ref acquisition, and no validation.

## State and Persistence Behavior

No state is created. It exposes an existing sub-FSAL handle pointer whose lifetime is tied to the MDCACHE entry.

## Dependencies and Integration Points

It includes `mdcache_int.h` and `mdcache_lru.h`. Integration is intended for debug and white-box testing code that already holds a reference on the MDCACHE object.

## Risks and Edge Cases

The returned sub-handle can be freed if the caller does not hold an MDCACHE ref for the full use duration. Using this helper in production paths bypasses MDCACHE coherency, accounting, and lock expectations.

## Test Signals

White-box tests can assert that a wrapped object maps to the expected lower FSAL handle while holding a ref. Static analysis should ensure production code does not depend on this header.
