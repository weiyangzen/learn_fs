# File Research: sources/os/linux/linux/fs/afs/fs_operation.c

## Purpose
Defines the lifecycle for fileserver-directed operations, including operation allocation, vnode I/O serialization, server iteration dispatch, completion handling, and cleanup.

## Main Responsibilities
- Allocates and initializes `struct afs_operation` objects against a volume and key.
- Provides a custom vnode I/O lock that can be handed between tasks without mutex ownership problems.
- Serializes operations on one or two vnodes in stable pointer order.
- Dispatches AFS or YFS RPCs through the operation’s `afs_operation_ops`.
- Applies success/aborted/failed callbacks and then releases all operation-owned references.

## Key Functions and Data
- `afs_alloc_operation()` pins the key and volume, snapshots volume callback/volsync state, and sets the initial error to `-EDESTADDRREQ`.
- `afs_begin_vnode_operation()` takes needed vnode I/O locks and snapshots fid/data-version/callback state.
- `afs_wait_for_operation()` loops through `afs_select_fileserver()`, issues RPCs, waits for calls, records response state, and invokes operation callbacks.
- `afs_end_vnode_operation()` drops I/O locks and dumps address-selection failures for relevant network errors.
- `afs_put_operation()` releases vnode refs, server state, server list, volume, key, and updates preferred address on successful response.
- `afs_do_sync_operation()` wraps begin, wait, and put for synchronous operations.

## Important Details
- Operations with held file locks are marked current-server-only in `afs_prepare_vnode()`.
- Modification operations set `AFS_VNODE_MODIFYING` and clear it in `afs_put_operation()`.
- Two-vnode lock acquisition orders by pointer value to avoid deadlocks.
