# File Research: sources/os/linux/linux-stable/fs/nfs/nfs4idmap.h

This header declares the NFSv4 idmapping interface used by NFS client setup and attribute decoding code.

Declarations:
- Lifecycle:
  - `nfs_idmap_init()`
  - `nfs_idmap_quit()`
  - `nfs_idmap_new()`
  - `nfs_idmap_delete()`
- Attribute owner/group string helpers:
  - `nfs_fattr_init_names()`
  - `nfs_fattr_free_names()`
  - `nfs_fattr_map_and_free_names()`
- Mapping APIs:
  - `nfs_map_name_to_uid()`
  - `nfs_map_group_to_gid()`
  - `nfs_map_uid_to_name()`
  - `nfs_map_gid_to_group()`
  - `nfs_map_string_to_numeric()`
- External tunable:
  - `nfs_idmap_cache_timeout`

Role:
- Keeps idmap implementation details out of users.
- Provides forward declarations for `nfs_client`, `nfs_server`, `nfs_fattr`, and `nfs4_string`.
- Includes UID/GID and UAPI idmap definitions.

Risk areas:
- This is a shared contract between idmap implementation, NFSv4 client setup, and XDR attribute decode/update code.
