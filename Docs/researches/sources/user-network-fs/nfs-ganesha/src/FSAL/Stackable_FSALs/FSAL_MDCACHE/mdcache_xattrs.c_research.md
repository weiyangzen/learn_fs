<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_xattrs.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_xattrs.c

## Purpose

This file implements the MDCACHE stackable FSAL extended-attribute operation vector. Every function is a thin pass-through from an MDCACHE object handle to the wrapped lower FSAL object handle. It covers both the older FSAL xattr API using `fsal_xattrent_t`/integer xattr IDs and the NFSv4.2-style named xattr operations using `xattrkey4`, `xattrvalue4`, `setxattr_option4`, cookies, and `xattrlist4`.

## Important APIs, Types, and Functions

- `struct mdcache_fsal_obj_handle`: recovered with `container_of(obj_hdl, ..., obj_handle)` and used to reach `handle->sub_handle`.
- `subcall(...)`: wraps lower-FSAL calls, preserving the MDCACHE stack's usual tracing/error behavior.
- Legacy xattr wrappers: `mdcache_list_ext_attrs`, `mdcache_getextattr_id_by_name`, `mdcache_getextattr_value_by_id`, `mdcache_getextattr_value_by_name`, `mdcache_setextattr_value`, `mdcache_setextattr_value_by_id`, `mdcache_remove_extattr_by_id`, and `mdcache_remove_extattr_by_name`.
- NFSv4 xattr wrappers: `mdcache_getxattrs`, `mdcache_setxattrs`, `mdcache_removexattrs`, and `mdcache_listxattrs`.

## Control Flow

Each function extracts the MDCACHE wrapper, invokes the corresponding `handle->sub_handle->obj_ops` method with the same arguments, stores the returned `fsal_status_t`, and returns it unchanged. There is no local validation, translation, name filtering, caching, cookie manipulation, or attribute invalidation visible in this file.

## State and Persistence Behavior

The file maintains no local persistent state. Extended attributes are stored and listed by the lower FSAL. MDCACHE object identity is only used to find the lower handle, so correctness depends on the wrapper handle lifetime and lower handle lifetime being synchronized elsewhere in MDCACHE.

## Dependencies and Integration Points

This file depends on FSAL public types, `mdcache_int.h`, and the lower FSAL's `obj_ops` implementation. It integrates with MDCACHE handle operation initialization elsewhere, where these functions are assigned into the MDCACHE object ops vector. The NFS protocol layer will observe whatever semantics the lower FSAL exposes, including support for NFSv4.2 xattrs.

## Risks and Edge Cases

- Since there is no local cache invalidation, any metadata cache consistency after xattr mutation must be handled by the lower FSAL, `subcall`, or surrounding MDCACHE code.
- The pass-through assumes `sub_handle` and each xattr method pointer are valid. Missing optional lower-FSAL xattr methods must be guarded before this layer or by default ops.
- The legacy ID-based xattr API is lower-FSAL-defined; MDCACHE does not stabilize IDs across calls.
- Return buffer sizing and cookie semantics are entirely delegated.

## Test Signals

Useful coverage includes xattr list/get/set/remove through an MDCACHE export backed by an xattr-capable FSAL, unsupported xattr operations backed by a lower FSAL without support, small-buffer `ERR_FSAL_TOOSMALL` behavior, list cookie continuation, and cache coherency checks where a set/remove is followed by get/list through the same MDCACHE object.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_xattrs.c -->
