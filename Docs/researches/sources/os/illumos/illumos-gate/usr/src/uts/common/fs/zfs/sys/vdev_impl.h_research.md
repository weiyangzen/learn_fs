# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/vdev_impl.h

This private header defines vdev operations, queues, caches, indirect state, the full `struct vdev`, persistent label layout, and internal vdev helper APIs.

Core definitions:
- `vdev_ops_t` contains type operations for open/close/asize/io start/done/state change/resilver need/hold/release/remap/xlate/dumpio plus type name and leaf flag.
- `vdev_cache_entry_t`, `vdev_cache_t`, `vdev_queue_class_t`, and `vdev_queue_t` define physical cache and queue scheduling state.
- `vdev_alloc_bias_t` distinguishes none, log, special, and dedup allocation classes.
- `vdev_indirect_config_t` records MOS object IDs for indirect mapping and birth arrays plus previous indirect vdev ID.
- `struct vdev` contains common identity/topology/state/stat fields, top-level metaslab fields, checkpoint/initialize/TRIM state, indirect/removal/obsolete fields, scan queue, leaf DTL/device/path/state/cache/queue/probe/MMP fields, and DTrace-sensitive final mutexes.
- Label constants define 256 KiB vdev labels, boot area offsets/sizes, uberblock ring layout, MMP slots, and boot envblock format.

Internal API surface:
- Allocate/free vdevs, manipulate parent/child topology, load/sync DTL and vdev state, dirty vdev components.
- Export ops structures for root, mirror, replacing, raidz, disk, file, missing, hole, spare, and indirect vdevs.
- Default size/xlate helpers and metaslab/vdev cache tunables.
- Indirect-vdev obsolete sync/condense helpers.
- Boot-from-ZFS disk label helper APIs.

Risk-sensitive invariants:
- `struct vdev` spans top-level, non-leaf, and leaf state; many fields are meaningful only for specific vdev kinds.
- Label geometry and uberblock offsets are persistent disk format.
- Indirect mapping pointers are protected by `vdev_indirect_rwlock`; obsolete segments have separate locking.
- Final DTrace-sensitive mutex fields must remain at the end for userland/kernel CTF compatibility.
