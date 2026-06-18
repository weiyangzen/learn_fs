# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev.c

## Role

`vdev.c` is the central ZFS virtual-device management implementation. It owns generic vdev tree construction, open/close/reopen, validation, probing, metaslab setup, DTL management, state transitions, statistics, space accounting, dirty-list syncing, expansion, splitting, and helper predicates used by the ZIO and SPA layers.

It dispatches type-specific behavior through `vdev_ops_table`, covering root, raidz, mirror, replacing, spare, disk, file, missing, hole, and indirect vdevs.

## Core Responsibilities

Vdev allocation and topology:
- `vdev_alloc_common()` initializes `vdev_t`, locks, queues, DTL range trees, vdev cache, trim/initialize state, indirect mapping fields, and generated GUIDs.
- `vdev_alloc()` parses config nvlists for type, GUID, log status, RAID-Z parity, allocation class bias, paths, devids, ashift, metaslab metadata, indirect mapping objects, top/leaf ZAPs, DTL objects, offline/fault/degrade/remove flags, resilver txg, and deferred resilver state.
- `vdev_add_child()`, `vdev_remove_child()`, and `vdev_compact_children()` maintain child arrays, parent links, top-vdev pointers, GUID sums, and the SPA leaf list.
- `vdev_add_parent()` and `vdev_remove_parent()` wrap or unwrap devices in mirror/replacing/spare parents while preserving top-level identity where required.
- `vdev_top_transfer()` moves top-level allocation, metaslab, checkpoint, dirty-list, log, allocation-bias, indirect-removal, and scan-queue state between top-level vdevs.

Opening and probing:
- `vdev_open_children()` opens children in parallel unless any path uses zvols, where opens are serialized to avoid namespace-lock issues.
- `vdev_open()` handles persistent fault/offline state, invokes the type-specific open op, normalizes sizes and ashift, validates minimum allocatable size, handles expansion/shrink, probes leaves, updates min/max ashift, and asks scan code whether resilver is needed.
- `vdev_probe()` reads and optionally writes label pad regions to confirm access. It coalesces probe storms by keeping one active probe zio per vdev.
- `vdev_validate()` reads labels and checks pool GUID, vdev GUID/top GUID, split-pool markers, pool state, txg selection for rewind, and corrupted-label cases before `vdev_load()` can repair against the wrong device.
- `vdev_validate_aux()` performs a simpler label sanity check for spares and L2ARC devices.

Metaslabs and space maps:
- `vdev_metaslab_set_size()` chooses metaslab size/count from vdev size, targeting roughly 200 metaslabs while bounding small and huge devices.
- `vdev_metaslab_group_create()` assigns top-level vdevs to normal, log, special, or dedup metaslab classes.
- `vdev_metaslab_init()` loads or creates metaslabs and activates the metaslab group unless the vdev is being removed.
- `vdev_metaslab_fini()` passivates and destroys loaded metaslabs and checkpoint space maps.
- `vdev_destroy_spacemaps()` frees metaslab space-map objects and the metaslab-array object.
- `vdev_load()` recursively loads children, deflate ratios, allocation bias, metaslabs, checkpoint space maps, DTLs, and obsolete space maps.

DTL behavior:
- The file documents the DTL model for missing, partial, scrub, and outage ranges.
- Only leaf `DTL_MISSING` is persisted; parent DTLs and outage maps are derived.
- `vdev_dtl_dirty()`, `vdev_dtl_contains()`, and `vdev_dtl_empty()` manipulate in-core DTL range trees.
- `vdev_dtl_reassess()` recomputes DTLs after config changes or scrub completion, including scrub excision with a reference tree.
- `vdev_dtl_load()` loads persisted leaf DTL space maps.
- `vdev_dtl_sync()` rewrites leaf DTL space maps, destroys them for detached/removed leaves, and dirties config if the object changes.
- `vdev_dtl_required()` temporarily marks a device unreadable to determine whether offlining/detaching/removing it would lose access to data.
- `vdev_resilver_needed()` returns whether writable leaves still have DTL ranges and reports min/max txg.

Sync and dirty state:
- `vdev_dirty()` puts top-level vdevs, metaslabs, DTL leaves, or indirect obsolete segments on txg dirty lists.
- `vdev_sync()` syncs obsolete segments, creates metaslab arrays, syncs dirty metaslabs and DTLs, removes empty log devices, and schedules clean callbacks.
- `vdev_sync_done()` completes metaslab sync and reassesses metaslab group state.
- `vdev_config_dirty()` and `vdev_state_dirty()` maintain SPA dirty lists for config and state changes.
- Aux vdev config dirtying updates the L2ARC/spare nvlist directly.

State transitions:
- `vdev_fault()`, `vdev_degrade()`, `vdev_online()`, `vdev_offline()`, and `vdev_clear()` implement administrative state changes.
- `vdev_fault()` backs off to degraded if faulting a required data device would lose data.
- `vdev_online()` clears offline state, can request expansion, restarts initialize/trim work, and supports unspare handling.
- `vdev_offline_locked()` prevents offlining required data devices, resets removable log devices, and reopens the top-level tree to verify survivability.
- `vdev_set_state()` handles removed/cant-open/fault/degrade/healthy transitions, leaf close-on-dead behavior, FMA ereports, not-present handling during import/recover, and parent propagation.
- `vdev_propagate_state()` aggregates child readability/writeability into parent state and treats top-level log device failures as root degradation.

Statistics and accounting:
- `vdev_get_stats_ex()` reports vdev state, size, expandable size, fragmentation, initialize progress, trim progress, deferred resilver, and queue/histogram stats.
- `vdev_stat_update()` records successful I/O ops, bytes, latency histograms, scan/self-heal counts, and failed read/write/checksum counts.
- Failed writes can dirty DTLs in the correct txg context, including scrub-thread repairs and ZIL claim repairs.
- `vdev_space_update()` updates top-level, class, and root alloc/space/dspace counters using the vdev deflate ratio.

Other helpers:
- `vdev_readable()`, `vdev_writeable()`, `vdev_allocatable()`, and `vdev_accessible()` gate I/O paths.
- `vdev_is_concrete()` excludes indirect, hole, missing, and root vdevs from allocation/write paths.
- `vdev_xlate()` recursively translates a child logical range into top-level physical range through vdev-specific xlate ops.
- `vdev_expand()` initializes new metaslabs after device growth.
- `vdev_split()` removes a child from a mirror-like topology during pool split.
- `vdev_deadman()` panics if active leaf I/O exceeds the pool deadman timeout.
- `vdev_replace_in_progress()` detects replacing/spare replacement activity.

## Integration Notes

This file sits between SPA config/state locking, ZIO I/O execution, metaslab allocation, DMU transactions, ZAP metadata, labels, FMA ereports, scan/resilver, initialize/trim, and indirect-vdev removal.

Edits here are high risk because small state, locking, txg, or dirty-list changes can affect import, resilver, device replacement, pool expansion, fault handling, and sync-time metadata persistence.

## Risk Notes

- Locking assumptions are strict: many functions assert `SCL_ALL`, `SCL_STATE_ALL`, `SCL_ALLOC`, or sync-context ownership.
- DTL updates must remain txg-correct or resilver/scrub behavior can silently lose repair coverage.
- `vdev_open()` and `vdev_validate()` intentionally separate accessibility from label identity; collapsing them risks I/O to the wrong device.
- Top-level transfer during attach/detach/replacement carries many metadata fields; omissions can orphan allocation or indirect-removal state.
- `vdev_stat_update()` intentionally suppresses speculative errors, retryable failfast EIO, and some root-level propagated errors; changing this affects user-visible pool health.
- Indirect, hole, missing, aux, log, and concrete vdev distinctions are woven through allocation, writeability, dirtying, sync, and state propagation.
