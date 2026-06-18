# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_acl.h

Defines ZFS ACL on-disk and in-memory structures. It covers legacy fixed-size ACE ACLs, newer FUID-aware variable-size ACEs, ACL node lists, ACL operation vectors, and create-time ACL identity bundles.

Key elements:
- `zfs_ace_hdr_t`, `zfs_ace_t`, `zfs_object_ace_t`, and `zfs_oldace_t` describe the supported ACE layouts.
- `zfs_acl_phys_v0_t` and `zfs_acl_phys_t` describe old and current ACL physical storage.
- `acl_ops_t` abstracts ACE accessors so ACL code can operate across ACE formats.
- `zfs_acl_t` and `zfs_acl_node_t` represent in-memory ACL chunks.
- `zfs_acl_ids_t` bundles owner/group FUIDs, mode, ACL, and FUID replay info for file creation.

Main dependencies and interactions:
- Depends on `sys/acl.h`, DMU, SA, and `zfs_fuid.h`.
- Used by znode creation, chmod/chown, access checks, ZIL ACL logging, and FUID replay.
- Kernel prototypes expose ACL conversion, allocation, access checking, inheritance transformation, external ACL lookup, and mode computation.

Implementation notes:
- ACL versioning is explicit: initial v0 ACLs use fixed `zfs_oldace_t`; FUID ACLs support variable-size entries.
- `ZFS_ACL_COUNT_SIZE` exists because the count field must be interpreted across both v0 and v1 layouts.
- The file is mostly ABI/structure contract; changing layouts would affect on-disk compatibility and replay.
