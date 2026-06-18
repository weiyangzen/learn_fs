# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_fuid.h

Defines FUID handling for ZFS identity mapping, including domain indexing, log replay support, and user/group/ACE identity categories.

Key elements:
- `zfs_fuid_type_t` distinguishes owner, group, ACE user, and ACE group.
- `FUID_INDEX`, `FUID_RID`, and `FUID_ENCODE` pack and unpack 64-bit FUIDs.
- `zfs_fuid_t` tracks converted ids and log-domain indexes.
- `zfs_fuid_domain_t` tracks unique domain strings.
- `zfs_fuid_info_t` accumulates FUID and domain data needed for create, setattr, and setacl logging/replay.

Main dependencies and interactions:
- Kernel mode depends on kidmap, SID, DMU, and `zfs_vfsops.h`.
- Closely tied to ACLs, ZIL replay, and filesystem FUID tables.
- Shared functions load and destroy FUID AVL tables.

Implementation notes:
- The header documents why FUID replay cannot depend on idmap availability and compresses unique domain strings in the log.
