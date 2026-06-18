# File Research: sources/virtualization/qemu/block/block-backend.c

This file implements QEMU's `BlockBackend`, the object that connects device models, monitor-owned block devices, jobs, throttling, permissions, AioContexts, media events, and the block graph's root `BlockDriverState`.

Core state:
- `BlockBackend` stores name/refcount/root child/AioContext, legacy drive info, public throttle member, attached device and callbacks, cached root state, write-cache setting, accounting stats, error policies, permissions, request queuing/drain state, VM-state handler, and in-flight AIO count.
- All BlockBackends are tracked in `block_backends`; monitor-visible ones are tracked separately in `monitor_block_backends`.
- The root BDS is attached through `child_root`, a `BdrvChildClass` with callbacks for media changes, resize, drain, activate/inactivate, attach/detach, AioContext migration, and parent naming.

Lifecycle:
- `blk_new()` creates a backend, initializes accounting, locks, queues, notifier lists, defaults error policy, and adds it to the global list.
- `blk_new_with_bs()` and `blk_new_open()` create backends around existing or newly opened BDS trees.
- `blk_ref()`/`blk_unref()` manage lifetime; final unref drains before deletion.
- `blk_delete()` removes the backend from global state, disables throttling, removes root BDS, removes VM state handler, checks notifier queues, cleans accounting, and frees memory.
- `monitor_add_blk()` and `monitor_remove_blk()` manage monitor-visible names and enforce id validity/name conflicts.

Root BDS management:
- `blk_insert_bs()` attaches a BDS as the root child with current or inactive permissions, notifies insert listeners, and moves throttle group AioContext.
- `blk_remove_bs()` notifies remove listeners, drains, saves root state, detaches throttling to main loop, clears `blk->root`, and unreferences the child under graph write lock.
- `blk_replace_bs()` delegates to `bdrv_replace_child_bs()`.
- `blk_update_root_state()` caches open flags and detect-zeroes for later reinsertion.

Permissions and migration:
- `blk_set_perm_locked()` applies permissions to the root child unless disabled.
- Incoming migration can temporarily disable permissions so storage migration/block jobs can still write.
- `blk_root_activate()` re-enables permissions after migration, temporarily shares all permissions, and defers final tightening if still in `RUN_STATE_INMIGRATE`.
- `blk_root_inactivate()` drops permissions for eligible guest devices/job backends.

Device model integration:
- `blk_attach_dev()` and `blk_detach_dev()` bind/unbind a `DeviceState`.
- `blk_set_dev_ops()` installs callbacks for media change, tray status, medium lock, resize, and drain.
- Media helpers emit `DEVICE_TRAY_MOVED` and call device callbacks.
- I/O status helpers track `OK`, `NOSPACE`, or `FAILED` when stop-on-error policy enables iostatus.

I/O data path:
- Coroutine APIs include read, write, write-zeroes, compressed write, discard, flush, ioctl, block status, allocation query, truncate, copy-range, zoned operations, and getlength/geometry.
- Each request generally increments `blk->in_flight`, waits while drained unless `BDRV_REQ_NO_QUEUE`, validates medium/offset/length through `blk_check_byte_request()`, applies throttling, delegates to the root child/BDS, then decrements in-flight.
- Write operations add `BDRV_REQ_FUA` when write cache is disabled.
- Asynchronous APIs wrap coroutine operations in `BlkAioEmAIOCB`, handle immediate coroutine completion with replay bottom halves, and keep in-flight accounting correct.
- `blk_abort_aio_request()` creates an async completion for immediate errors such as no medium.

Drain and quiescing:
- `blk_root_drained_begin()` increments the quiesce counter, calls device `drained_begin`, and disables/restarts throttling.
- `blk_wait_while_drained()` queues coroutines while drained, carefully dropping in-flight only after taking `queued_requests_lock`.
- `blk_root_drained_poll()` reports busy if device callbacks or in-flight requests remain.
- `blk_root_drained_end()` re-enables queued requests, restoring in-flight for each resumed coroutine.
- `blk_drain()` and `blk_drain_all()` wait for BDS drain and backend-only in-flight completions.

AioContext handling:
- `blk_get_aio_context()` returns the atomic backend context.
- `blk_set_aio_context()` handles empty backends directly or asks the BDS graph to move context with temporary permission to change.
- `blk_root_change_aio_ctx()` rejects active/attached backends unless explicitly allowed, and commits context changes through a transaction.
- AioContext notifier add/remove functions mirror notifications onto the current root BDS.

Error policy:
- `blk_get_error_action()` maps read/write `BlockdevOnError` policy and errno into report/stop/ignore.
- `blk_error_action()` sets iostatus, orders `BLOCK_IO_ERROR` before VM stop, and requests `RUN_STATE_IO_ERROR` when policy is stop.

Limits and memory:
- Helpers expose request alignment, write-zero alignment, max hardware transfer, max transfer, max iov, and block-aligned allocation.
- `blk_register_buf()`/`blk_unregister_buf()` forward registered-buffer lifecycle to the root BDS when present.
- `blk_root()` exposes the root child.

Filesystem/block relevance:
- This is one of QEMU's central block abstractions: guest devices and management code use `BlockBackend`, while image/protocol drivers live below it as BDS nodes.
- It is responsible for translating guest-facing block operations into graph operations with permissions, drains, throttling, accounting, and media semantics.

Potential pitfalls:
- Many APIs require the right execution domain (`GLOBAL_STATE_CODE`, `IO_CODE`, graph read/write locks).
- Drain accounting is subtle because some in-flight completions can exist without a root BDS.
- AioContext changes are constrained for active backends; callers must opt in carefully.
