# File Research: sources/os/linux/linux-stable/fs/afs/fs_operation.c

## Summary
Provides the common operation wrapper for fileserver-directed AFS operations. It allocates operation state, serializes vnode I/O, prepares vnode parameters, drives server/address rotation through RPC issue callbacks, applies success/failure hooks, and releases all operation-owned resources.

## Main Responsibilities
- Allocates and initializes `struct afs_operation`.
- Implements a custom per-vnode I/O serialization lock.
- Locks one or two vnodes for operations in stable pointer order.
- Captures pre-operation vnode status, data version, and callback break state.
- Waits for fileserver selection and RPC completion.
- Runs operation-specific success, abort, failure, and directory-edit hooks.
- Tears down operation references and updates preferred address hints.

## Key APIs
- `afs_alloc_operation()`.
- `afs_begin_vnode_operation()`.
- `afs_wait_for_operation()`.
- `afs_end_vnode_operation()`.
- `afs_put_operation()`.
- `afs_do_sync_operation()`.

## Important Behavior
`afs_alloc_operation()` pins the key and volume, snapshots volume callback and volsync state, assigns a debug id, and starts with cumulative error `-EDESTADDRREQ`.

The I/O lock is implemented with `AFS_VNODE_IO_LOCK`, a waiters list, task wakeups, and release/acquire memory barriers. This is used instead of a normal mutex because operations may unlock from a different thread context.

`afs_wait_for_operation()` repeatedly asks `afs_select_fileserver()` for a viable server/address, issues the AFS or YFS RPC, waits for call completion, records call error/abort/responded state, then invokes operation callbacks based on cumulative result.

## State and Synchronization
Operations may hold `AFS_OPERATION_LOCK_0` and `AFS_OPERATION_LOCK_1`. Modification operations set `AFS_VNODE_MODIFYING` during preparation and clear it in `afs_put_operation()`. More-than-two vnode operations store additional vnode params in `op->more_files`.

## Risks
The custom I/O lock is easy to misuse: waiter removal, signal interruption, and lock transfer must remain paired. Operation cleanup owns many heterogeneous references: calls, server state arrays, server lists, volumes, keys, inodes, and optional operation payloads.
