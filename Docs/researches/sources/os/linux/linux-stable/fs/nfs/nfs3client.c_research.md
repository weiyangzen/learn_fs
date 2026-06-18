# File Research: sources/os/linux/linux-stable/fs/nfs/nfs3client.c

## Purpose
Provides NFSv3-specific server/client creation helpers, NFSACL client setup, and pNFS data server client setup for NFSv3.

## ACL Client Setup
- Under `CONFIG_NFS_V3_ACL`, defines `nfsacl_program` using `nfsacl_version3`.
- `nfs_init_server_aclclient()`
  - Skips setup if `NFS_MOUNT_NOACL`.
  - Binds the NFSACL program to the main server RPC client.
  - Links the ACL RPC client into sysfs.
  - Sets `NFS_CAP_ACLS` on success, clears it on failure.
- Without ACL support, clears ACL capability and normalizes flags.

## Server Creation
- `nfs3_create_server(struct fs_context *fc)`
  - Calls common `nfs_create_server()`.
  - Initializes ACL client when server creation succeeds.
- `nfs3_clone_server(...)`
  - Calls common `nfs_clone_server()`.
  - Initializes ACL client for cloned server if source has a usable ACL client.

## pNFS Data Server Client
- `nfs3_set_ds_client(...)`
  - Builds `nfs_client_initdata` for an NFSv3 data server.
  - Uses MDS identity, net namespace, credentials, and timeout policy.
  - Computes connect/reconnect timeout from DS timeo/retrans.
  - Fakes hostname from DS address for lockd.
  - Handles TCP-TLS fallback to TCP unless MDS transport security is configured.
  - Carries `nconnect` for TCP/RDMA families when MDS has multiple connections.
  - Propagates no-reserved-port and net-unreachable-fatal flags.
  - Marks the client as a data server with `NFS_CS_DS`.
  - Calls `nfs_get_client()`.

## Research Notes
The ACL setup here pairs with `nfs3acl.c` and `nfs3xdr.c`. The pNFS data-server path is carefully conservative: soft-ish low timeout behavior is chosen so failures can fall back through the metadata server.
