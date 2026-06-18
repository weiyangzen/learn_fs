# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_defer.h

## Scope

This header declares the deferred-operation framework data structures, operation-type callback table, exported defer op types, resource capture state, recovery APIs, pause flag, and cache lifecycle functions.

## Main Interfaces

- `struct xfs_defer_pending` stores one pending deferred operation group, its work items, log intent, log done item, operation type, count, and flags.
- `XFS_DEFER_PAUSED` marks pending work that should be carried forward without finishing.
- `struct xfs_defer_op_type` defines callbacks for intent creation/abort, done creation, item finishing, cleanup, cancellation, recovery, and relogging.
- Exports operation types for bmap, refcount, realtime refcount, rmap, realtime rmap, extent free, AGFL free, realtime extent free, attr, and exchange mappings.
- `struct xfs_defer_resources` tracks buffers and inodes held across transaction rolls.
- `struct xfs_defer_capture` stores detached deferred ops plus reservations and held resources for recovery continuation.
- Inline `xfs_defer_add_item()` appends a work item and increments the count.

## Dependencies

Forward declares btree cursor, defer op type, and capture structures, and relies on transaction, log item, list, buffer, and inode types from the broader XFS kernel environment.

## Risks And Invariants

- `max_items` constrains log reservation sizing for each operation type.
- Callback contracts are strict: finish callbacks may request continuation with `-EAGAIN`, cleanup must release operation-specific state, and recovery callbacks own recovered pending records.
- Resource capture supports up to five inodes and two buffers, chosen for complex rename/parent-pointer deferred operations.
- Paused work must not have unresolved data dependencies because it can be requeued indefinitely.
