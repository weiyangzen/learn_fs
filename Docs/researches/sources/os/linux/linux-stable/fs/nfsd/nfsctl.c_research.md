# File Research: sources/os/linux/linux-stable/fs/nfsd/nfsctl.c

## Summary
Implements NFSD’s administrative control surface. It backs the `nfsd` pseudo-filesystem transaction files, legacy `/proc/fs/nfs/exports`, generic netlink control operations, per-network-namespace NFSD initialization, and module init/exit.

## Main APIs
- nfsdfs transaction handlers: `write_filehandle()`, `write_unlock_ip()`, `write_unlock_fs()`, `write_threads()`, `write_pool_threads()`, `write_versions()`, `write_ports()`, `write_maxblksize()`.
- NFSv4 controls: lease time, grace time, legacy recovery dir, and `v4_end_grace`.
- nfsdfs client control directories: `nfsd_client_mkdir()`, `nfsd_client_rmdir()`, `get_nfsdfs_client()`.
- Generic netlink handlers: RPC status dump, thread set/get, version set/get, listener set/get, and pool mode set/get.
- Lifecycle: `nfsd_net_init()`, `nfsd_net_exit()`, `init_nfsd()`, `exit_nfsd()`.

## Behavior
Legacy transaction files parse text commands for threads, pool threads, versions, listener sockets/transports, filehandle generation, block size, and NFSv4 timing. Netlink provides structured replacements for server configuration, listener management, protocol version toggles, pool mode, and live RPC status reporting. Mounting `nfsd` creates control files and a `clients` directory used by NFSv4 client-state observability.

## State and Synchronization
Most service mutation is serialized by `nfsd_mutex`. Listener list surgery also uses `svc_serv->sv_lock`. Per-net setup creates export/idmap caches, proc stats, counters, callback state, write-verifier state, optional localio state, and optional filehandle signing keys. RPC status dump reads service threads under RCU and validates request fields with `rq_status_counter`.

## Risks
This file is the administrative choke point: callers must preserve the “server stopped” checks for version, lease, grace, scope, and filehandle-key changes. Listener replacement is intentionally conservative because deleting listeners while threads are active is rejected. Filehandle signing depends on `nn->fh_key` being configured before signed handles are verified or emitted.
