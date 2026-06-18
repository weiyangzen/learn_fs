# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_indirect_births.c

## Role

`vdev_indirect_births.c` manages the side table that records physical birth txgs for ranges in an indirect vdev mapping. This lets ZFS determine when a remapped range was copied during vdev removal.

## Main Behavior

Lifecycle:
- `vdev_indirect_births_alloc()` allocates a DMU metadata object with a bonus buffer containing `vdev_indirect_birth_phys_t`.
- `vdev_indirect_births_open()` holds the bonus buffer, points at the physical header, and reads all birth entries into memory when count is nonzero.
- `vdev_indirect_births_close()` frees the in-memory entry array, releases the bonus buffer, clears pointers, and frees the handle.
- `vdev_indirect_births_free()` frees the DMU object.

Accessors:
- `vdev_indirect_births_count()` returns entry count.
- `vdev_indirect_births_object()` returns the backing object number.
- `vdev_indirect_births_last_entry_txg()` returns the last entry’s physical birth txg.

Mutation:
- `vdev_indirect_births_add_entry()` appends `{max_offset, txg}` to the DMU object, increments the bonus-buffer count, and rebuilds the in-memory array with the appended entry.
- It requires syncing context and a syncing DMU transaction.

Lookup:
- `vdev_indirect_births_physbirth()` binary-searches entries to return the physical birth txg for a contiguously mapped range.
- Each entry implicitly describes the range from the previous entry’s offset to its own offset.
- The lookup asserts the requested `offset + asize` fits within the selected entry boundary.

## Integration Notes

This file is used by indirect-vdev removal/remap code alongside `vdev_indirect_mapping`. It depends on DMU object allocation, bonus buffers, sync-context transactions, and in-memory copies of fixed-size physical entries.

## Risk Notes

- Entries must remain sorted by increasing offset and physical birth txg.
- The binary search relies on implicit previous-entry boundaries, so a simple independent-entry search would be wrong.
- Lookups require the requested range to be contiguously mapped and within the last recorded offset.
- `add_entry()` rewrites the in-memory array on every append; this is simple but assumes append frequency and size remain manageable.
- Verification asserts object, objset, dbuf, physical header, and entry-array consistency.
