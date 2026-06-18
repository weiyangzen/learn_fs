# File Research: sources/os/linux/linux/fs/ceph/snap.c

CephFS snapshot realm management and cap-snapshot coordination. This file maintains the client-side hierarchy of `ceph_snap_realm` objects, builds per-realm `ceph_snap_context` arrays, handles MDS snapshot notifications, queues inode cap snapshots when contexts change, and manages snapid-to-anonymous-block-device mappings.

Key responsibilities:
- Reference and lifetime management for snap realms via `ceph_get_snap_realm()`, `ceph_put_snap_realm()`, `__destroy_snap_realm()`, and empty-realm cleanup.
- Realm lookup/creation in `mdsc->snap_realms`, keyed by realm inode number.
- Parent/child realm topology updates through `adjust_snap_realm_parent()`.
- Snap context construction in `build_snap_context()`, merging parent snaps newer than `parent_since`, realm-local snaps, and prior-parent snaps, then reverse-sorting snap IDs.
- Downward rebuild traversal in `rebuild_snap_realms()` after realm topology or snap-set changes.
- MDS snap trace decode/apply in `ceph_update_snap_trace()`.
- Creation/finalization/flush queuing of `ceph_cap_snap` records for inodes with dirty caps or dirty/writeback data.
- Snap message handling in `ceph_handle_snap()`, including split-realm migration of inodes and child realms.
- Snapid map allocation, LRU trimming, and cleanup for snapshot device mapping.

Important data/control flow:
- MDS supplies snap traces; the client decodes each encoded `ceph_mds_snap_realm`, updates realm sequence/snaps/parent fields, rebuilds contexts, and queues cap snapshots for dirty realms.
- For a new snapshot, `queue_realm_cap_snaps()` walks all inodes with caps in the affected realm and calls `ceph_queue_cap_snap()`.
- `ceph_queue_cap_snap()` captures inode metadata, xattr blob/version, issued/dirty cap bits, and dirty-page counts under the inode’s previous snap context.
- `__ceph_finish_cap_snap()` records final size/timestamps/version/truncate state and adds the inode to `mdsc->snap_flush_list` once dirty data is gone.
- `flush_snaps()` drains `mdsc->snap_flush_list` by calling `ceph_flush_snaps()`.

Concurrency/lifetime notes:
- Realm topology operations require `mdsc->snap_rwsem`, with write locking for mutation.
- Realm inode lists use `realm->inodes_with_caps_lock`.
- Snap flush queue uses `mdsc->snap_flush_lock`.
- Empty realm destruction uses `snap_empty_lock` around 0-ref transitions to avoid races between re-acquire and deferred cleanup.
- Split handling uses inode `i_ceph_lock` while moving an inode between realms.
- Snapid maps use `snapid_map_lock`, refcounts, rb-tree lookup, and LRU timeout (`CEPH_SNAPID_MAP_TIMEOUT`).

Failure handling:
- Allocation failures during context build clear stale cached contexts and leave rebuild to later.
- Corrupt snap traces fence client I/O via `CEPH_MOUNT_FENCE_IO`, try to blocklist the client, and warn that remount is required.
- `ceph_handle_snap()` closes sessions when `ceph_update_snap_trace()` fails.

Notable observation:
- `ceph_update_snap_trace()` accepts a `deletion` parameter and comments mention avoiding cap-snap queuing on delete, but this file’s visible implementation does not branch on that parameter.
