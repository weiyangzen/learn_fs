# sources/user-network-fs/samba/source3/modules/vfs_default_quota.c

## Purpose
`vfs_default_quota.c` maps Windows default quota values onto real user/group quota records so Samba can expose default quotas on filesystems that lack native default quota storage.

## Important APIs, Types, And Functions
The module registers `default_quota_get_quota()` and `default_quota_set_quota()`. Config macros read `default_quota:uid`, `uid nolimit`, `gid`, and `gid nolimit`. Default FS quota requests are translated to configured user/group quota records, root by default.

## Control Flow
Get operations delegate first, then rewrite default user/group FS quota requests by reading the configured uid/gid quota while preserving qflags. Protected configured uid/gid records can be reported as no-limit. Set operations reject protected records when `nolimit` is enabled, delegate the original set, then mirror default FS quota updates into the configured real quota record.

## State And Persistence
No private state is kept. Default quota data persists in the underlying quota database for the configured uid/gid.

## Dependencies And Integration Points
The module depends on Samba quota types, `SMB_QUOTAS_SET_NO_LIMIT()`, lower quota VFS hooks, and optional group quota compile support.

## Risks
Using real quota records as metadata can affect real accounts if misconfigured. Some failure returns do not explicitly set errno. If lower layers reject default FS quota types, the mirror write may not happen. Group behavior depends on compile-time support.

## Test Signals
Test user and group default quota read/write mapping, protected no-limit behavior, qflags preservation, non-root storage IDs, ENOSYS lower layers, and Windows quota UI behavior.
