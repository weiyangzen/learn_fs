# File Research: sources/os/linux/linux-stable/fs/ceph/quota.c

## Purpose

`quota.c` implements CephFS quota handling in the kernel client. It receives quota updates from MDS, tracks hidden quota realm inodes, checks file and byte quota limits through snap realm ancestry, compares quota realms for rename/link decisions, and adjusts statfs output for mounted roots constrained by quota.

## Major Responsibilities

- Maintains `mdsc->quotarealms_count` with `ceph_adjust_quota_realms_count()`.
- Quickly decides whether quota checks may be needed with `ceph_has_realms_with_quotas()`.
- Handles `CEPH_MSG_CLIENT_QUOTA` messages by finding the target inode and updating recursive bytes/files/subdirs plus max byte/file quota fields.
- Maintains an rb-tree of `struct ceph_quotarealm_inode` for quota realm inodes that are outside the visible mountpoint.
- Looks up hidden quota realm inodes and caches failures for 60 seconds to avoid repeated useless requests.
- Cleans hidden quotarealm inode cache during pre-umount.
- Walks snap realm ancestry to find the nearest realm with relevant quota, optionally dropping and reacquiring `snap_rwsem` to look up hidden realm inodes.
- Compares whether two inodes belong to the same quota realm.
- Checks max-files and max-bytes quota exceedance.
- Checks whether max-bytes quota is approaching, using a threshold of writes consuming more than 1/16 of remaining quota space.
- Updates `statfs` block counts when the mounted root is under a max-bytes quota.

## Key Algorithms

- `get_quota_realm()` starts from an inode's snap realm, walks parents, obtains each realm inode, checks `__ceph_has_quota()`, and returns the first matching realm or the root realm.
- `check_quota_exceeded()` walks the same realm hierarchy and tests each realm's recursive usage against `i_max_files` or `i_max_bytes`.
- `ceph_quota_is_same_realm()` needs two realm lookups under a consistent snap view. If the second lookup has to drop `snap_rwsem`, it returns `-EAGAIN` and restarts.
- `ceph_quota_update_statfs()` converts quota bytes and recursive bytes into reported block/free counts, with special handling for quotas smaller than the normal Ceph block size and smaller than 4 KiB.

## Concurrency and Lifetime Notes

- Uses `mdsc->snap_rwsem` to protect snap realm traversal.
- Temporarily drops `snap_rwsem` around hidden inode lookup when needed, then restarts traversal to avoid stale realm state.
- Uses `realm->inodes_with_caps_lock` to safely access realm inode pointers.
- Uses inode `i_ceph_lock` while reading or updating quota and recursive usage fields.
- Hidden quotarealm inode cache is protected by `quotarealms_inodes_mutex`, with per-entry mutexes for lookup/update serialization.

## Edge Cases

- Snapshotted inodes are treated as not quota-checkable for enforcement paths.
- If `i_snap_realm` is temporarily `NULL` after caps are released, quota checks treat it as no quota found or not exceeded.
- Reserved MDS stray inodes are exempt from quota realm detection.
- If the mount root is not the real CephFS root, the client conservatively assumes quota realms may exist even if the local count is zero.
- Quota usage can exceed quota; statfs reports zero free blocks in that case.

## Research Notes

This file bridges MDS-maintained recursive quota accounting with local VFS decisions. The delicate part is realm traversal under `snap_rwsem` while sometimes needing to perform inode lookups that require dropping that lock.
