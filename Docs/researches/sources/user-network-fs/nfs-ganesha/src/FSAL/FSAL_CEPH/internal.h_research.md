# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_CEPH/internal.h

## Purpose

`internal.h` is the private Ceph FSAL contract shared by module, export, handle, pNFS, and compatibility code. It defines module state, shared mount state, export state, object handles, fd/state wrappers, pNFS DS wire structures, supported/settable attribute masks, error conversion, and internal prototypes. The complete 286-line file was read for this report.

## Important APIs, Types, and Functions

Key types are `struct ceph_fsal_module`, `struct ceph_mount`, `struct ceph_export`, `struct ceph_fd`, `struct ceph_state_fd`, `struct ceph_join_deleg_arg`, `struct ceph_host_handle`, `struct ceph_handle_key`, `struct ceph_handle`, and under `CEPH_PNFS`, `struct ds_wire` and `struct ds`. It declares `construct_handle`, `deconstruct_handle`, `attrmask2ceph_want`, `ceph2fsal_attributes`, `export_ops_init`, `handle_ops_init`, pNFS ops initializers, `ceph_alloc_state`, ACL helpers, mount AVL helpers, and delegation helpers.

## Control Flow

This header has no executable flow beyond the inline `ceph2fsal_error` converter. It establishes how implementation files exchange ownership: module code creates `ceph_export` and shared `ceph_mount`, export code resolves paths and filehandles, handle code operates on `ceph_handle`, and internal code initializes/finalizes those structures.

## State and Persistence Behavior

The definitions describe all long-lived Ceph FSAL state. `ceph_fsal_module` stores global configuration flags (`client_oc`, `async`, `zerocopy`, reclaim/service registration options). `ceph_mount` is shared by exports and owns the libcephfs mount, refcount, mount key, delegation flags, and current upcall export. `ceph_export` owns export config and root handle. `ceph_handle` owns the libcephfs inode pointer, global fd, cache key, share state, and optional pNFS counters. Persistent identity is represented by packed inode/snap/fscid fields plus export id in the handle key.

## Dependencies and Integration Points

It includes libcephfs, FSAL public/private headers, UUID support, statx compatibility, commonlib, and AVL tree support. All Ceph FSAL implementation files depend on this header, and compile-time features (`CEPH_PNFS`, `CEPHFS_POSIX_ACL`, `USE_FSAL_CEPH_LL_DELEGATION`) alter the exposed state and prototypes.

## Risks and Edge Cases

Packed filehandle structs are wire/cache ABI and must not change casually. Secrets are present in `ceph_mount` keys and must be freed correctly and not logged. The pNFS declarations in this header do not align cleanly with some references in `mds.c` in the inspected tree, which is a compile-risk when `CEPH_PNFS` is enabled. The inline error converter assumes Ceph errors are negative POSIX values.

## Test Signals

Test signals are compile coverage across feature macros, structure-size and filehandle round-trip checks, static assertions or ABI checks for packed handle fields, mount refcount transitions, pNFS builds, ACL-enabled and ACL-disabled builds, async/zerocopy configuration, and leak checks for user id, secret key, mount path, and root handles during export teardown.
