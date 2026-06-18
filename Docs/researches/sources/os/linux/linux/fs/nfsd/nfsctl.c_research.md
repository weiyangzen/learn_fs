# File Research: sources/os/linux/linux/fs/nfsd/nfsctl.c

## Summary
Implements the administrative control surface and module lifecycle for the in-kernel NFS server. It backs the `nfsd` pseudo-filesystem, legacy proc exports view, generic netlink server management APIs, per-net namespace initialization, and module init/exit sequencing.

## Main Responsibilities
- Defines transaction-style control files such as `threads`, `pool_threads`, `versions`, `portlist`, `max_block_size`, `filehandle`, lock unlock helpers, NFSv4 lease/grace controls, and cache/stat files.
- Mounts and populates the `nfsd` filesystem with control files, export views, stats, optional Kerberos enctype symlink, and `clients/` debug directories.
- Provides generic netlink handlers for server threads, listeners, enabled protocol versions, pool mode, filehandle signing key, server scope, lease/grace settings, and live RPC status dumps.
- Initializes and destroys per-network-namespace NFSD state, including exports, idmapping, proc stats, counters, callback state, localio lists, write verifier state, and filehandle signing key memory.
- Performs module-level setup and teardown for debugfs, NFSv4 slabs/pNFS/laundry work, duplicate reply cache slab, lockd callbacks, export workqueue, pernet ops, client tracking, filesystem registration, netlink family registration, proc entries, and localio hooks.

## Key Data Structures and Interfaces
- `write_op[]` maps pseudo-file inode numbers to transaction handlers.
- `transaction_ops` uses `simple_transaction_*` so reads can synthesize zero-length writes and writes return generated replies.
- `nfsd_files[]` describes the pseudo-filesystem entries and their file operations.
- `nfsd_genl_*` handlers encode and decode generic netlink attributes defined by the NFSD netlink family.
- `nfsdfs_client` references are attached to inodes under `nfsd/clients/` and released through recursive removal callbacks.
- `nfsd_net_ops` allocates per-net `struct nfsd_net` state and registers `nfsd_net_id`.

## Important Behavior
Writes to `threads` and netlink `threads_set` call `nfsd_svc()` under `nfsd_mutex`, so listener setup, version state, thread counts, and server lifetime are serialized. `pool_threads` adjusts per-pool maxima but cannot fully start the server from zero and preserves at least one thread in pool zero when used.

`versions` and netlink version configuration reject changes while `nn->nfsd_serv` exists. Text configuration supports `+N`, `-N`, and NFSv4 minor forms; netlink clears current versions then applies nested major/minor enabled attributes.

`portlist` supports three modes: read current listener names, add an existing socket file descriptor, or create IPv4/IPv6 listeners from a transport name and port. Netlink listener configuration can replace listener sets, but removing listeners is blocked while threads are active.

NFSv4 lease and grace times are bounded to 10 through 3600 seconds and are mutable only while the service is down. `v4_end_grace` allows explicit grace termination only via affirmative writes.

The RPC status dump walks all service pools and threads under RCU while using `rq_status_counter` acquire loads to avoid reporting unstable request fields. For NFSv4 compounds it includes a bounded list of operation numbers.

Filehandle signing keys are copied from netlink as two little-endian u64 values into a per-net `siphash_key_t`; setting is restricted to stopped service state by the caller.

## Dependencies
Depends on SunRPC service and transport APIs, lockd, rpc_pipefs/GSS, export and idmap caches, NFSD NFSv4 state and pNFS initialization, duplicate reply cache, filecache stats, procfs, generic netlink, fs context APIs, pernet operations, localio, and tracepoints.

## Risks and Subtleties
Most mutation paths rely on `nfsd_mutex`; adding new control paths without the same locking can race service creation, listener replacement, or version changes. The text pseudo-file ABI has legacy parsing behavior and user-visible compatibility quirks, especially around NFSv4 version reporting and transaction reads.

Listener replacement is delicate: old sockets are temporarily spliced away, possible deletes are blocked with active threads, then missing requested sockets are recreated. Error handling must avoid leaving an empty stopped service object around.

Per-net teardown frees sensitive `fh_key` memory and destroys counters/caches; lifecycle changes must preserve init/exit unwind ordering because many later resources depend on earlier pernet, workqueue, slab, and callback setup.
