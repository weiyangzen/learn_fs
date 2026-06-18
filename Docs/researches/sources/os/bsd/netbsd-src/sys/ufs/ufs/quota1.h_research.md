# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/quota1.h

This header defines the original deprecated UFS disk quota format.

Key contents:
- Defines default soft-limit grace periods for block and inode quotas.
- Defines legacy quota filename and group.
- Defines old `quotactl` command encoding and commands.
- Defines `struct dqblk`, the on-disk quota1 record indexed by uid/gid.
- Declares conversion helpers between `dqblk` and generic `quotaval` pairs.

Role:
- Compatibility support for legacy quota files with 32-bit counters and limits.
