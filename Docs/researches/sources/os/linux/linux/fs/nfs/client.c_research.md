# File Research: sources/os/linux/linux/fs/nfs/client.c

## Purpose
Manages shared NFS client records, per-mount server records, RPC clients, NFS version registration, server probing, network namespace NFS client lists, and `/proc` reporting for mounted NFS servers and volumes.

## Main Responsibilities
- Register and find NFS protocol version modules.
- Allocate, share, initialize, reference, and destroy `nfs_client` objects.
- Create base RPC clients and per-server cloned RPC clients.
- Initialize NFSv2/v3 server records from mount context.
- Probe FSINFO/PATHCONF and derive server capabilities and I/O sizes.
- Start lockd for NFSv2/v3 when needed.
- Allocate, insert, remove, clone, and free `nfs_server` records.
- Initialize and destroy per-network-namespace NFS client state.
- Expose `/proc/fs/nfsfs` and `/proc/net/nfsfs` server/volume listings.

## Key Functions
- `find_nfs_version()`, `register_nfs_version()`, and `unregister_nfs_version()` manage NFS version modules and RPC version tables.
- `nfs_alloc_client()` initializes a shared client with address, hostname, version ops, transport settings, net namespace, and localio state.
- `nfs_get_client()` finds an existing matching client or allocates/inserts/initializes a new one.
- `nfs_put_client()` drops references and destroys clients when the count reaches zero.
- `nfs_create_rpc_client()` creates the base SUNRPC client using mount transport/security settings.
- `nfs_init_server_rpcclient()` clones the base client with selected auth flavor for a mounted server.
- `nfs_init_server()` initializes NFSv2/v3 mount server data.
- `nfs_probe_fsinfo()` performs capability, FSINFO, PATHCONF, and trunking discovery.
- `nfs_create_server()` creates a root server record for a mount.
- `nfs_clone_server()` creates a server record for referrals/submounts.
- `nfs_clients_init()` and `nfs_clients_exit()` manage per-net lists and callback IDR state.

## Client Sharing Rules
`nfs_match_client()` matches on protocol version ops, transport protocol, NFSv4 minor version, data-server flag, address or xprt-switch address, and transport security policy/cert identities. Clients still initializing are waited on before reuse.

## Server Initialization Flow
`nfs_create_server()` allocates `nfs_server`, gets credentials, allocates fattr storage, initializes the server/client/RPC state from mount context, probes FSINFO, sets NFSv2/v3 name and readdirplus caps, fetches attributes if needed, stores FSID, inserts the server into global lists, and returns the mounted server record.

## FSINFO Behavior
`nfs_server_set_fsinfo()` derives read/write sizes, page counts, write multipliers, directory transfer size, max file size, change attribute type, clone block size, socket buffers, and NFSv4.2 xattr sizes/capability. Mount options clamp or override many of these values.

## Data and Ownership
- `nfs_client` is refcounted and freed via version-specific `free_client`.
- `nfs_server` is RCU-freed after RPC clients, credentials, sysfs state, and client refs are released.
- Net namespace lists are protected by `nn->nfs_client_lock`.
- Server-to-client list membership uses RCU for callback/layout/delegation iteration.

## Notable Details
- `nfs_mark_client_ready()` uses memory barriers around `cl_cons_state` and wakes waiters.
- NFSv2/v3 lockd is skipped when both local flock and local fcntl are requested.
- NFSv4 capability initialization is delegated to minor-version ops and then adjusted for mount flags and transport constraints.
- Localio support initializes client UUID/boot state and schedules asynchronous probing when enabled.
- `/proc` server and volume views print transport address, port, refcount, hostname, device, FSID, and fscache state.

## Risks and Edge Cases
- Matching clients while another thread initializes requires careful wait/retry behavior to avoid duplicate clients or use of failed clients.
- Error paths in server creation must avoid double-putting partially initialized RPC clients and client refs.
- FSINFO sizes are bounded by RPC payload and NFS max I/O constants; incorrect server values are clamped.
- `nfs_alloc_server()` frees `server` directly if iostat allocation fails but does not free the allocated sysfs ID in that path, which is worth verifying against surrounding code expectations.

## Integration Points
This is central NFS client infrastructure used by NFSv2/v3/v4 mount code, callback lookup, delegation/layout iteration, pNFS, lockd, SUNRPC, sysfs, fscache, localio, and procfs reporting.
