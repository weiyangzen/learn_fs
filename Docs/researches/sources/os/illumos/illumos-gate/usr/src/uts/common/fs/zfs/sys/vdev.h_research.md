# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/vdev.h

This public header declares the virtual-device interface: lifecycle, DTLs, state, metaslabs, stats, labels, queue/cache, and config generation.

Core definitions:
- `vdev_dtl_type_t` enumerates missing, partial, scrub, outage, and count DTLs.
- Global `zfs_nocacheflush` controls cache flush behavior.
- `vdev_config_flag_t` marks spare, L2ARC, removing, MOS, and missing config generation modes.
- `vdev_labeltype_t` describes label initialization reasons: create, replace, spare, remove, L2ARC, and split.

Public API surface:
- Vdev debug, open/validate/create/reopen/close/probe, path copy, zvol-use detection, concrete/bootable checks, lookup/count helpers.
- DTL dirty/contains/empty/need-resilver/reassess/required/resilver-needed APIs.
- ZAP link management, spacemap destruction, obsolete marking, replacement progress, vdev hold/release.
- Metaslab init/fini/size/expand/split/deadman/xlate APIs.
- Stats update/get/clear/scan init/propagate/set-state/children-offline helpers.
- Space accounting, deflation, psize-to-asize, fault/degrade/online/offline/clear, liveness/readable/writeable/allocatable/accessibility checks.
- Cache and queue init/fini/read/write/purge/IO/priority helpers.
- Config/state dirty/clean/sync, deferred resilver, config generation, label offsets/config/uberblock load/bootenv read/write/label init.

Risk-sensitive invariants:
- DTLs are central to resilver safety and replication accounting.
- Label routines operate on persistent disk labels and bootenv data.
- Vdev state changes must coordinate with SPA config/state locks and dirty lists.
