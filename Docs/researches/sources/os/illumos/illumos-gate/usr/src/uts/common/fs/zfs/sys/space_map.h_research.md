# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/space_map.h

This header defines ZFS space maps: on-disk append logs of allocated/free ranges plus in-core handles for loading, writing, truncating, and histogram maintenance.

Core definitions:
- `space_map_phys_t` contains legacy object field, object length, allocated-space count, padding, and 32-bucket histogram.
- `space_map_t` records the logical region start/size, unit shift, objset/object/blocksize, dbuf, and physical bonus pointer.
- `maptype_t` distinguishes `SM_ALLOC` and `SM_FREE`.
- `space_map_entry_t` is the decoded entry form: type, optional vdev ID, offset, and run length in `sm_shift` units.
- Encoding macros define debug entries, single-word entries, and two-word entries, including offset/run/vdev/type limits.

Public API surface:
- Entry classification helpers for debug/single/double word entries.
- Load full or length-limited spacemaps into range trees, iterate entries, and incrementally destroy.
- Histogram verify/clear/add helpers.
- Accessors for object, allocated space, length, entry count, and block count.
- Write range-tree deltas, estimate optimal size, truncate, allocate/free objects, open/close handles.

Risk-sensitive invariants:
- Space maps are not internally concurrent; callers provide synchronization.
- Two-word entries must not straddle block boundaries; padding uses debug entries.
- `smp_histogram` is allocator-visible and may include log-spacemap unflushed changes for metaslab spacemaps.
- Offsets and runs are encoded in `sm_shift` units and must respect single/two-word maximums.
