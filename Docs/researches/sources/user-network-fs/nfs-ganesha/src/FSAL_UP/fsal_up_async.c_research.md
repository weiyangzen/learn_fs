## sources/user-network-fs/nfs-ganesha/src/FSAL_UP/fsal_up_async.c

### Purpose
`fsal_up_async.c` provides asynchronous wrappers for FSAL upcalls and related callback work. It copies request arguments into heap allocations, queues work on a `fridgethr`, invokes the synchronous upcall implementation in a worker context, calls optional completion callbacks, and releases references.

### Important APIs, Types, And Functions
Async FSAL upcall wrappers include `up_async_invalidate`, `up_async_update`, `up_async_lock_grant`, `up_async_lock_avail`, `up_async_layoutrecall`, `up_async_notify_device`, and `up_async_delegrecall`. Protocol/internal async helpers include `async_cbgetattr`, `async_delegrecall_per_state`, and `async_delegrecall`. Each wrapper has a corresponding queued function such as `queue_invalidate`, `queue_update`, `queue_lock_grant`, `queue_layoutrecall`, `queue_notify_device`, `queue_cbgetattr`, `queue_delegrecall_per_state`, `queue_delegrecall`, or `up_queue_delegrecall`.

### Control Flow
Each upcall wrapper allocates an args struct, copies scalar parameters and file/object handle bytes into flexible array storage where needed, submits to `fridgethr_submit`, frees the args on submit failure, and returns either an FSAL status converted from POSIX submit status or a raw int for internal helpers. Queue callbacks call through `vec->up_fsal_export->up_ops` for invalidate/update/lock/layout/delegation/device work, invoke optional callbacks with FSAL or state status, and free args. `async_cbgetattr`, `async_delegrecall_per_state`, and `async_delegrecall` take object/client/state/export references before queueing and release them in the queued function or submit-failure path.

### State And Persistence
The file maintains no global state. It transfers ownership of heap-allocated argument blocks to fridge worker callbacks and temporarily holds object, state, client ID, and export references to keep asynchronous work safe after the caller returns.

### Dependencies And Integration Points
It depends on NFS core structures, FSAL upcall vectors, SAL functions, pNFS utilities, `fridgethr_submit`, and error conversion from `fsal_convert.c`. It integrates backend FSAL upcalls with MDCACHE/SAL operations such as invalidation, attribute updates, lock notifications, layout recall/device notifications, callback getattr, and delegation recall.

### Risks
The file comments say every async call takes an export reference, but several vector-based wrappers only store `vec` and have an `XXX` comment about export refcounting for delegation recall; callers must ensure `vec` and its export remain alive until queued work runs. `up_async_update` shallow-copies `struct fsal_attrlist`, so embedded allocations such as ACLs or buffers must remain valid or be immutable until execution. Owner and cookie pointers for lock/layout operations are copied as pointers, not deep-copied. Queue failure paths are mostly balanced, but any newly added argument type must mirror reference cleanup exactly.

### Test Signals
Tests should cover successful queue execution and submit failure for each wrapper, callback invocation status, deep-copy behavior for handle buffers, object/client/state/export refcount balance, layout recall with and without `layoutrecall_spec`, notify-device parameter propagation, and lifetime safety when exports or states are concurrently released.
