# File Research: sources/os/linux/linux/fs/nfs/nfs3client.c

## Purpose
Provides NFSv3-specific server/client setup, including the optional NFSACL RPC client and pNFS data server client creation.

## Key Functions
- `nfs_init_server_aclclient()` binds the NFSACL program to the server RPC client unless `NFS_MOUNT_NOACL` is set; on success, marks `NFS_CAP_ACLS`.
- `nfs3_create_server()` wraps generic server creation and initializes the ACL client.
- `nfs3_clone_server()` clones a server and initializes ACL support on the clone when the source has it.
- `nfs3_set_ds_client()` builds a pNFS data server `nfs_client` for NFSv3, using MDS identity/net/credentials, soft timeout settings, DS flags, optional TLS inheritance, `nconnect`, noresvport, and network-unreachable fatal behavior.

## Research Notes
The pNFS DS path is the nuanced part: it deliberately uses short soft timeouts so data server failures can be retried through the metadata server.
