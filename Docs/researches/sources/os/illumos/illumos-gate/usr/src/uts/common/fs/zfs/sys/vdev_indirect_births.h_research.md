# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/vdev_indirect_births.h

This header declares the birth-time side table for indirect vdev mappings created during device removal.

Core definitions:
- `vdev_indirect_birth_entry_phys_t` stores a source offset boundary and physical birth TXG.
- `vdev_indirect_birth_phys_t` stores the number of birth entries.
- `vdev_indirect_births_t` stores object ID, in-memory sorted entry array, objset, dbuf, and bonus pointer.

Public API surface:
- Open/close/is-open, allocate/free object, count/object accessors.
- Add an entry for an offset and TXG.
- Query physical birth for a range and get the last entry TXG.

Risk-sensitive invariants:
- Entries are sorted by increasing physical birth and offset; lookup semantics depend on "everything up to but not including offset" boundaries.
- Birth TXGs determine whether remapped data is old enough for a given block pointer or rewind context.
