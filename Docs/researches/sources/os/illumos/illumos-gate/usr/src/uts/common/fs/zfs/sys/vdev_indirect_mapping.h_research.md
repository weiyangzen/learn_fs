# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/vdev_indirect_mapping.h

This header declares indirect vdev mapping objects, used to translate offsets from removed vdevs to replacement DVAs.

Core definitions:
- `vdev_indirect_mapping_entry_phys_t` stores encoded source offset/mark in `vimep_src` and destination DVA in `vimep_dst`.
- `DVA_MAPPING_GET_SRC_OFFSET()` and `DVA_MAPPING_SET_SRC_OFFSET()` encode/decode source offsets in SPA minimum-block units.
- `vdev_indirect_mapping_entry_t` wraps a physical entry with obsolete-count and list linkage for pending updates.
- `vdev_indirect_mapping_phys_t` stores max offset, bytes mapped, entry count, and obsolete-counts object.
- `vdev_indirect_mapping_t` stores object ID, whether counts exist, sorted in-memory entry array, objset, dbuf, and bonus pointer.

Public API surface:
- Open/close, allocate/free mapping object.
- Query entry count, max offset, object ID, bytes mapped, and mapping size.
- Add pending mapping entries from a list.
- Find mapping entry for an offset or the next mapping entry at/after an offset.
- Load, populate, increment, and free obsolete-count arrays from obsolete spacemaps.

Risk-sensitive invariants:
- Mapping entries are sorted by source offset and DVA ASIZE limits individual mapped ranges.
- Obsolete counts are used during indirect-vdev condense and must remain aligned with mapping entries.
- The high source-offset mark bit is reserved for garbage collection tooling.
