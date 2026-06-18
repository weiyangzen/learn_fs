# File Research: sources/local-fs/xfsprogs/libxfs/defer_item.c

Userspace deferred-operation item implementation for libxfs.

Key responsibilities:
- Provides defer add/finish/cancel operation types for extent frees, realtime extent frees, AGFL frees, rmap updates, realtime rmap updates, refcount updates, realtime refcount updates, bmap updates, logged attrs, and exchange mappings.
- Sorts deferred items by AG/rtgroup or inode where needed.
- Holds group intent references across deferred transaction rolls.
- Finishes each item by calling the corresponding libxfs operation.
- Requeues partially completed operations with `-EAGAIN`.
- Provides log intent space calculation helpers even though userspace does not log actual intents.

Important behavior:
- Intent/done creation and abort functions are dummies because libxfs tools do not perform kernel logging.
- Realtime and data-section rmap/refcount updates use separate defer operation types to avoid AGF/realtime metadata lock mixing.
- Bmap map intents pre-account delayed blocks and undo that on cancellation.
- Attribute intents initialize per-operation attr state machines and run `xfs_attr_set_iter`.

Dependencies:
- Deeply tied to libxfs allocation, rmap, refcount, bmap, attr, exchange-map, group, rtgroup, and transaction code.

Notable risks:
- Correct cancellation is essential because many items own group references and slab-cache allocations.
- Requeue behavior depends on callee mutation of remaining block counts.
