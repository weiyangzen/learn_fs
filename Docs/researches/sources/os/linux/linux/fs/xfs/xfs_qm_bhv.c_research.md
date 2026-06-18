# File Research: sources/os/linux/linux/fs/xfs/xfs_qm_bhv.c

## Role

Mount/statvfs behavior helpers for quotas. It translates project quota limits into statfs-style results and validates/restores quota state during mount.

## Main Responsibilities

- `xfs_fill_statvfs_from_dquot` clamps `kstatfs` block and inode totals/free counts to the applicable dquot hard or soft limits.
- `xfs_qm_statvfs` reports project-quota constrained `statvfs` for directory trees using inherited project IDs.
- `xfs_qm_validate_state_change` rejects quota state changes on read-only or norecovery mounts.
- `xfs_qm_newmount` reconciles requested mount quota flags with on-disk quota accounting flags, optionally mounts quotas immediately if no quotacheck is required, or defers quota mounting by clearing `m_qflags`.
- `xfs_qm_resume_quotaon` restores accounting/enforcement state from the superblock for metadata-directory filesystems when no quota mount options were supplied.

## Important Behavior

Project quota-backed directory trees are presented as filesystem-like accounting domains to `df`/`statfs`. Mounts that would require quota state mutations are rejected when transactions cannot safely be written.

## Dependencies

Uses mount flags, quota flags, dquot lookup, inode/project IDs, transactions indirectly through `xfs_qm_mount_quotas`, and generic `kstatfs`.
