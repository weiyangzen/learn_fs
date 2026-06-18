# File Research: sources/virtualization/qemu/block/snapshot.c

Provides block-layer internal snapshot management helpers. It defines snapshot option descriptors, lookup helpers by name or by ID/name, and generic wrappers for create, goto, delete, list, temporary load, and grouped all-device snapshot operations.

For drivers without native snapshot callbacks, the code can fall back to a primary child only when it is safe: the node must have a primary child and no other data/metadata/filtered children that would also need snapshotting. Fallback snapshot goto is more involved: it references the fallback child, closes the parent, detaches the child, applies the snapshot to the child, clears parent opaque state, reopens the parent with options forcing the same child node, and then unreferences the child.

`bdrv_can_snapshot()`, `bdrv_snapshot_create()`, `bdrv_snapshot_delete()`, `bdrv_snapshot_list()`, and `bdrv_snapshot_goto()` all prefer driver callbacks and otherwise use the safe fallback path. Snapshot goto rejects active dirty bitmaps. Temporary snapshot load requires a read-only device and a driver-provided `bdrv_snapshot_load_tmp`.

The all-device helpers collect either explicit node names or all BDS nodes, include writable inserted nodes that are in use by a `BlockBackend` or monitor-owned root nodes, and then check/create/delete/goto snapshots across that set. Delete drains all devices while operating. VM state snapshot selection finds either a named node or the first snapshot-capable included node.
