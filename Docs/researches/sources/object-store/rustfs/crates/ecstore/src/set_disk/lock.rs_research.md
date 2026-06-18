# sources/object-store/rustfs/crates/ecstore/src/set_disk/lock.rs

## Purpose
Collects namespace-lock error mapping plus disk membership, online-disk selection, reconnection, and endpoint renewal for a `SetDisks` shard. It is the bridge between logical object operations and the mutable runtime health of drives.

## Important APIs, Types, And Functions
Lock helpers are `format_lock_error`, `format_lock_error_from_error`, and `map_namespace_lock_error`, with quorum failures mapped to `StorageError::NamespaceLockQuorumUnavailable`. Disk selection helpers include `get_disks_internal`, `get_local_disks`, `get_online_disks`, `get_online_local_disks`, `drive_membership_snapshot`, and `get_online_disks_with_healing_and_info`. Reconnection uses `connect_disks`, `renew_disk`, `connect_endpoint`, and `find_disk_index`.

## Control Flow
Online selection builds a `DriveMembershipSnapshot`, filters strict online or scanner/heal candidates, randomizes order, probes `disk_info` through the metadata processor, orders non-scanning disks before scanning and healing disks, and performs one runtime reprobe if all candidates initially fail. `connect_disks` closes bad or unlocated disks and calls `renew_disk` for their endpoints. `renew_disk` reconnects, loads format metadata, finds the disk’s expected set/disk index by UUID, enables health checks, updates global local-disk maps for distributed erasure, and swaps the disk into `self.disks`.

## State And Persistence Behavior
This file mutates in-memory disk membership, health-check state, and global local-disk maps. It reads persisted `format.json` through `load_format_erasure` to validate disk identity before reattaching a drive.

## Dependencies And Integration Points
It depends on `rustfs_lock`, `DriveMembershipSnapshot`, endpoint construction, global local disk state, distributed-erasure mode, format loading, `send_heal_disk`, and processor pools. All set-disk operations use these helpers to choose candidates and renew failed drives.

## Risks
Holding write access while awaiting `disk_info` in `get_online_disk_with_healing_and_info` can serialize or block other disk state operations. Correctness depends on keeping `DiskInfo` aligned with shuffled disks; the newer processor path explicitly preserves submitted indexes. Global map mutation can race with other initialization or renewal paths if assumptions drift.

## Test Signals
Tests cover disk/info alignment after shuffling, membership filtering of suspect/returning/offline states, one-shot reprobe recovery, and health monitoring on renewed disks. These are strong regression signals for this file’s highest-risk behaviors.
