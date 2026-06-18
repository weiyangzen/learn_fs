# File Research: sources/os/linux/linux/fs/nfs/nfs4idmap.h

This header declares the NFSv4 idmapping interface used by client setup and attribute decode/update code.

Declarations:
- Lifecycle: `nfs_idmap_init()`, `nfs_idmap_quit()`, `nfs_idmap_new()`, and `nfs_idmap_delete()`.
- Attribute owner/group string helpers: `nfs_fattr_init_names()`, `nfs_fattr_free_names()`, and `nfs_fattr_map_and_free_names()`.
- Mapping APIs: `nfs_map_name_to_uid()`, `nfs_map_group_to_gid()`, `nfs_map_uid_to_name()`, `nfs_map_gid_to_group()`, and `nfs_map_string_to_numeric()`.
- External tunable: `nfs_idmap_cache_timeout`.

Role:
- Keeps idmap implementation details out of callers.
- Provides forward declarations for `nfs_client`, `nfs_server`, `nfs_fattr`, and `nfs4_string`.
- Includes UID/GID and NFS idmap UAPI definitions.

Risk areas:
- This header is a shared contract between idmap implementation, NFSv4 client setup, and XDR attribute decode/update paths.
- Signature drift would affect multiple translation and mount paths.
