# File Research: sources/os/linux/linux-stable/fs/nfs/client.c

## Purpose

`client.c` implements core NFS client and server-instance management. It registers NFS protocol versions, allocates and shares `nfs_client` records, creates RPC clients, initializes per-mount `nfs_server` records, probes filesystem/server capabilities, tracks servers in per-net lists, exposes `/proc` views, and tears resources down.

## Main Responsibilities

- Maintain the global NFS RPC program version table and load protocol-version modules on demand.
- Allocate, initialize, match, reference, and free shared `struct nfs_client` objects.
- Create base RPC clients with mount/session transport settings and security policy.
- Initialize v2/v3 client state and lockd integration.
- Initialize per-mount `struct nfs_server` records from `fs_context`.
- Probe FSINFO/PATHCONF and derive I/O sizes, capabilities, max file size, xattr sizes, and cache timings.
- Allocate/free server records, I/O stats, sysfs IDs, RPC clients, and lockd state.
- Clone server records for submounts/referrals.
- Maintain per-network-namespace NFS client/server lists and procfs views.

## Key Functions

- `find_nfs_version()` returns a referenced protocol module, requesting `nfsv<version>` if needed.
- `register_nfs_version()` and `unregister_nfs_version()` publish/remove protocol implementations under `nfs_version_lock`.
- `nfs_alloc_client()` initializes a shared client object, including address, hostname, version module, transport settings, net namespace reference, and optional localio state.
- `nfs_get_client()` finds a matching initialized client or allocates/inserts a new one.
- `nfs_match_client()` compares version ops, transport protocol, minor version, DS flag, address/xprt switch addresses, and transport security policy.
- `nfs_create_rpc_client()` builds `rpc_create_args` from client init data and mount flags, then stores the base RPC client.
- `nfs_init_server_rpcclient()` clones the base RPC client with the selected auth flavor for a mounted server.
- `nfs_init_server()` configures a v2/v3 server from mount context, starts lockd, creates the RPC client, sets initial caps, and records mountd options.
- `nfs_probe_fsinfo()` and `nfs_server_set_fsinfo()` fetch server FSINFO/PATHCONF and compute effective NFS I/O parameters.
- `nfs_alloc_server()` initializes all per-server lists, delegation state, pNFS queues, I/O stats, owner counters, and wait queues.
- `nfs_create_server()` creates a v2/v3 mounted server, probes FSID and attributes, inserts it into lists, and records mount time.
- `nfs_clone_server()` duplicates a server record with a new filehandle/auth flavor and probes capabilities.
- `nfs_clients_init()` and `nfs_clients_exit()` manage per-net list heads, locks, stats, v4 caches, and sysfs state.
- Procfs helpers expose `/proc/net/nfsfs/servers`, `/proc/net/nfsfs/volumes`, and compatibility symlinks under `/proc/fs/nfsfs`.

## Control Flow and State

`nfs_client` objects are shared across mounts that match transport, NFS version, minor version, DS role, server address/xprt switch, and transport security. Creation uses a two-phase pattern: allocate outside the per-net spinlock, insert while marked initializing, then run protocol-specific `init_client()`. Other callers that find an initializing client take a reference, drop the lock, and wait on `nfs_client_active_wq`.

Each mount gets an `nfs_server` with its own cloned RPC client and mount-specific flags, auth, attribute cache parameters, FSID, capabilities, sysfs identity, delegation lists, layout lists, and stats. Server records are linked into both the owning client's superblock list and the per-net volume list under `nfs_client_lock`.

## Integration Points

- Uses protocol-specific `nfs_rpc_ops` for client allocation/init, fsinfo/pathconf/getattr, capabilities, trunking discovery, and lockd callbacks.
- Integrates with SUNRPC clients, stats, metrics, xprt security, TCP/TLS/RDMA transports, and optional localio.
- Initializes pNFS server queues and delegation structures used by other files in this group.
- Exposes sysfs links through NFS sysfs helpers.
- Integrates with lockd for NFSv2/v3 advisory locking.

## Risks and Edge Cases

- Client sharing must be exact enough to avoid cross-mount security or transport-policy leaks; TLS X.509 serials are part of the match.
- Initialization failure is stored in `cl_cons_state` and must wake waiters; callers must check readiness before using clients.
- `nfs_alloc_server()` allocates a sysfs ID before I/O stats; if I/O stats allocation fails, the shown path frees the server but does not visibly free the allocated ID in that branch.
- Server list removal uses `synchronize_rcu()`, so teardown can block waiting for readers.
- Procfs iteration holds `nfs_client_lock` while formatting entries and uses RCU around peer address string access.

## Testing Focus

Test version module loading/unloading, client matching across address/xprt-switch/TLS cases, concurrent mounts racing on one initializing client, RPC client flag construction, v2/v3 lockd setup, FSINFO-derived I/O clamping, server creation error unwinds, clone server setup, per-net init/exit warnings, and procfs output with live mounts.
