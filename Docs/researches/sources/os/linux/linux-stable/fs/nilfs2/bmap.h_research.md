# File Research: sources/os/linux/linux-stable/fs/nilfs2/bmap.h

Purpose: defines NILFS2 block-map data structures, operation table, pointer allocation helpers, dirty-state helpers, conversion thresholds, and public bmap APIs.

Key structures and state:
- `union nilfs_bmap_ptr_req` represents either a raw pointer or a persistent allocator request for DAT-backed virtual block allocation.
- `struct nilfs_bmap_stats` records created/deleted block counts.
- `struct nilfs_bmap_operations` defines backend callbacks for lookup, contiguous lookup, insert/delete, clear, dirty propagation, dirty-buffer collection, disk block assignment, mark, seek/last key, and private conversion checks/data gathering.
- `struct nilfs_bmap` is the in-memory mapping object with raw on-disk payload, rwsem, owner inode, backend ops, allocation target cache, pointer type, state flags, and node fanout.
- Pointer types distinguish physical, single-version virtual, multi-version virtual, and unmanaged pointer handling.
- `struct nilfs_bmap_store` is a shadow copy used to save/restore bmap raw data, allocation target, and dirty state.

Major logic:
- Declares the public bmap API for lookup, contiguous lookup, insert, delete, truncate, clear, propagate, dirty-buffer lookup, assign, mark, initialization, read/write, GC initialization, save, and restore.
- Inline pointer helpers prepare/commit/abort DAT-backed virtual pointer allocation/end operations, or update local sequential physical allocation state when no DAT is used.
- `nilfs_bmap_set_target_v()` stores a preferred virtual allocation target.
- Dirty helpers test, set, and clear `NILFS_BMAP_DIRTY` under the assumption the bmap semaphore is already locked.
- Defines direct-vs-btree size thresholds: small direct key range and large btree key range.

Concurrency and lifetime:
- Comments require callers of dirty helpers to hold the bmap semaphore.
- Pointer allocation helpers must be paired with commit/abort just like allocator requests.
- DAT-backed helpers pass through to DAT transaction APIs and respect single-version versus multi-version end semantics.

Important dependencies:
- Includes NILFS on-disk format definitions, allocator, and DAT APIs.
- Used by direct, btree, metadata, inode, segment, and garbage-collection code.

Risk/edge cases:
- `NILFS_BMAP_NEW_PTR_INIT` uses the high bit of `unsigned long`; pointer arithmetic must preserve the “new pointer” marker behavior.
- Mixing pointer types would corrupt metadata because physical and virtual pointer lifecycles differ.
- Conversion constants must stay consistent with direct and btree backend capacities.
