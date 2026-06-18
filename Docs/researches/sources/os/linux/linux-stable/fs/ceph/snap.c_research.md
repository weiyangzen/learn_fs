# File Research: sources/os/linux/linux-stable/fs/ceph/snap.c

## Purpose
Implements CephFS client-side snapshot realm tracking, snap context construction, cap-snap queuing/flushing, MDS snapshot notification handling, and snapid-to-device mappings for snapped inode presentation.

## Main Interfaces
- Realm references and lookup: `ceph_get_snap_realm()`, `ceph_put_snap_realm()`, `ceph_lookup_snap_realm()`, `ceph_cleanup_global_and_empty_realms()`.
- MDS trace/update handling: `ceph_update_snap_trace()`, `ceph_handle_snap()`.
- Inode realm movement: `ceph_change_snap_realm()`.
- Cap-snap lifecycle: `__ceph_finish_cap_snap()`, internal `ceph_queue_cap_snap()`, `queue_realm_cap_snaps()`, `flush_snaps()`.
- Snap device map: `ceph_get_snapid_map()`, `ceph_put_snapid_map()`, `ceph_trim_snapid_map()`, `ceph_cleanup_snapid_map()`.

## Control Flow
Snapshot state is represented as a hierarchy of `ceph_snap_realm` objects keyed by realm inode number in `mdsc->snap_realms`. MDS snap traces update realm parentage, snap lists, prior-parent snap lists, creation sequence, and realm sequence. When a realm or one of its ancestors changes, `rebuild_snap_realms()` walks downward and `build_snap_context()` composes a reverse-sorted `ceph_snap_context` from parent snaps after `parent_since`, explicit realm snaps, and prior-parent snaps.

When new contexts are built, dirty realms are queued and all inodes with caps in those realms get cap-snap processing. `ceph_queue_cap_snap()` snapshots inode metadata/xattr state when dirty caps, buffered writes, or in-progress writes must be associated with the old snap context. `__ceph_finish_cap_snap()` finalizes size/time/truncate/change metadata once writes and dirty pages are done, then places the inode on `mdsc->snap_flush_list` for `ceph_flush_snaps()`.

`ceph_handle_snap()` decodes MDS snapshot messages. For `CEPH_SNAP_OP_SPLIT`, it moves listed inodes and child realms into a new realm before applying the snap trace. Corrupt snap traces fence I/O, try to blocklist the client, warn, and require remount after MDS-side repair.

## State And Synchronization
Realm topology is protected by `mdsc->snap_rwsem`; zero-reference realms are staged on `mdsc->snap_empty` under `snap_empty_lock` when immediate destruction cannot take the write semaphore. Inodes are attached to realm `inodes_with_caps` lists under per-realm spinlocks and inode `i_ceph_lock`. Cap-snap flushing uses `mdsc->snap_flush_lock`.

The snapid map uses an rb-tree plus LRU list under `snapid_map_lock`, allocates anonymous block devices via `get_anon_bdev()`, and trims unused mappings after `CEPH_SNAPID_MAP_TIMEOUT`.

## Integration Points
Depends on MDS client message decoding, inode/cap code, `ceph_flush_snaps()`, OSD writeback paths, `ceph_monc_blocklist_add()`, and snapshot context APIs from libceph. It is central to write ordering across distributed CephFS snapshots.

## Risks And Review Focus
- Realm reference transitions are subtle because 0-to-1 and 1-to-0 must coordinate with `snap_empty_lock`.
- Snap trace corruption deliberately fences client I/O; decode bounds and error paths are high-impact.
- Cap-snap creation must preserve metadata exactly at the snapshot boundary despite concurrent writes and writeback.
- Split handling races with other MDS notifications and must avoid moving inodes from newer realms.
