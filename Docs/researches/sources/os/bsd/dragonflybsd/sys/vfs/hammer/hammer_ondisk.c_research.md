# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_ondisk.c

## Purpose
Provides the residency and access layer for HAMMER on-disk structures: volumes, translated filesystem buffers, B-tree nodes, allocation helpers, and filesystem sync queuing.

## Key Elements
- Maintains RB trees for installed volumes, cached buffers, and cached B-tree nodes.
- `hammer_install_volume()` opens a device, validates or formats the volume header, checks FSID/volume numbering, inserts the volume, and records the root volume.
- Provides volume reference/load/release/unload paths around embedded `hammer_io`.
- `hammer_get_buffer()` resolves zone offsets through blockmap or undo mappings, handles read-only raw-zone aliases, creates cached `hammer_buffer` structures, and loads/new-zeros backing buffers.
- `hammer_sync_buffers()` flushes dirty/running HAMMER buffers that could alias direct frontend reads.
- `hammer_del_buffers()` destroys or invalidates buffers over a range after block reuse or direct writes.
- Exposes `hammer_bread()`, `hammer_bread_ext()`, `hammer_bnew()`, and `hammer_bnew_ext()` for offset-based buffer access.
- `hammer_get_node()` and related node functions cache B-tree nodes separately from buffers, validate node CRCs, support passive node caches, and flush node references when buffers disappear.
- Allocation helpers create B-tree nodes and allocate data in metadata, small-data, or large-data zones according to record type and size.
- Sync helpers scan vnodes, call `VOP_FSYNC`, and trigger async or synchronous flusher passes.

## Dependencies
Uses DragonFlyBSD namei/vnode/buffer APIs, HAMMER I/O primitives, blockmap/undo translation, CRC validation, volume numbering, flusher APIs, vnode sync scanning, and B-tree node/buffer data structures from `hammer.h`.

## Behavior/Risks
The layer relies on 0-to-1 reference transitions to load on-disk state and on final release to hand buffers back to the I/O subsystem. Read-only mounts may see zone aliases from recovery and handle them specially. CRC-bad B-tree nodes return `EIO` or `EDOM` depending on transaction flags. Unmount paths deliberately avoid flushing dirty buffers that should already have been handled by the flusher.
