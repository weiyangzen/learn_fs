# File Research: sources/os/linux/linux/fs/ceph/quota.c

Implements CephFS quota handling, quota realm discovery, quota checks, hidden realm inode lookup, and statfs quota reporting.

Key behavior:
- Maintains `mdsc->quotarealms_count` when inodes gain or lose max-bytes/max-files quota state.
- Quickly decides whether quota checks may be needed based on known quota realm count, whether the mount root is the real CephFS root, and whether the inode is reserved/stray.
- Handles MDS quota messages by finding the target inode and updating recursive bytes/files/subdirs plus max bytes/files under the inode Ceph lock.
- Maintains an rb-tree of `ceph_quotarealm_inode` entries for quota realm inodes not visible from the current mountpoint.
- Looks up hidden quota realm inodes by ino, caches successful inodes, retries getattr when cached inodes exist but lack caps, and throttles failed lookups for 60 seconds.
- Cleans all cached quota realm inode records during MDS client pre-umount.
- Walks an inode’s snaprealm ancestry to find the nearest realm with the requested quota type, returning the root realm if no quota is found before root.
- Temporarily drops and reacquires `snap_rwsem` when hidden realm inode lookup is required; callers can request restart behavior with the `retry` argument.
- Compares whether two inodes belong to the same quota realm, restarting if snap realm lookup had to drop `snap_rwsem`.
- Checks max-files quota for new file creation by walking realm ancestors and testing recursive file/subdir usage plus one.
- Checks max-bytes quota for writes by comparing new file growth against recursive bytes usage.
- Checks max-bytes “approaching” threshold when a write would consume more than 1/16 of remaining quota space, using reported size as the baseline.
- Updates `statfs` output for a mounted root with max-bytes quota, converting quota bytes to block counts, handling quotas smaller than 4 MiB with 4 KiB block sizing, and reporting zero free space when exceeded.

Important interactions:
- Called from `mds_client.c` on `CEPH_MSG_CLIENT_QUOTA`.
- Uses quota helpers and declarations in `super.h`, including `__ceph_has_quota()` and `__ceph_update_quota()`.
- Depends on snaprealm state maintained by `snap.c` and protected by `mdsc->snap_rwsem`.
- Used by create/write/statfs paths to enforce or report CephFS quota limits.
