# File Research: sources/os/linux/linux/fs/gfs2/quota.h

Declares the GFS2 quota subsystem API and quota helper constants.

Key contents:
- Defines `NO_UID_QUOTA_CHANGE` and `NO_GID_QUOTA_CHANGE` sentinels.
- Declares qadata allocation/refcount helpers, quota hold/unhold, quota lock/unlock, quota check/change, sync/refresh/init/cleanup, quotad, and statfs wakeup APIs.
- Provides `gfs2_quota_lock_check()`, which bypasses quota checks for quota-off or `CAP_SYS_RESOURCE`, otherwise locks quota data and enforces limits unless in account-only mode.
- Exposes `gfs2_quotactl_ops`, quota-data shrinker init/exit, global quota-data LRU, and quota hash initialization.

This header is used by allocation and mount paths to integrate quota checks with block reservation. Its important contract is that successful `gfs2_quota_lock_check()` may leave quota data locked and must be paired with `gfs2_quota_unlock()` by the caller.
