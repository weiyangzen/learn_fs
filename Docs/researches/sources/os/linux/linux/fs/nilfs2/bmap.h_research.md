# File Research: sources/os/linux/linux/fs/nilfs2/bmap.h

`bmap.h` defines NILFS2 block mapping data structures, operation tables, pointer types, dirty state helpers, and public bmap APIs.

Important structures:
- `union nilfs_bmap_ptr_req` wraps either a raw bmap pointer or a persistent allocator request.
- `struct nilfs_bmap_stats` tracks block creation/deletion counts.
- `struct nilfs_bmap_operations` is the polymorphic interface implemented by direct and B-tree backends. It includes lookup, contiguous lookup, insert, delete, clear, propagate, dirty-buffer collection, block assignment, GC marking, seek/last-key, and private conversion helper hooks.
- `struct nilfs_bmap` stores raw on-disk mapping data, an rw semaphore, owner inode, operation table, last allocated key/ptr hints, pointer type, state flags, and child capacity.
- `struct nilfs_bmap_store` is a snapshot used for save/restore of raw mapping data and allocation/dirty state.

Pointer modes:
- `NILFS_BMAP_PTR_P`: physical block number.
- `NILFS_BMAP_PTR_VS`: virtual block number, single version.
- `NILFS_BMAP_PTR_VM`: virtual block number, multiple versions.
- `NILFS_BMAP_PTR_U`: pointer operations disabled.
- `NILFS_BMAP_USE_VBN()` identifies virtual pointer modes.

Inline helpers:
- New-pointer marker detection.
- Normal lookup at level 1.
- Prepare/commit/abort allocation and end-of-life pointer handling, delegating to DAT when present or manipulating local allocation hints otherwise.
- Target-virtual-pointer hint update.
- Dirty-state test/set/clear helpers, assuming the bmap semaphore is held.

Constants define the inline bmap storage size, dirty flag, small/direct and large/B-tree key ranges, and conversion threshold flag. This header is the common contract used by NILFS direct, B-tree, DAT, metadata, and GC code.
