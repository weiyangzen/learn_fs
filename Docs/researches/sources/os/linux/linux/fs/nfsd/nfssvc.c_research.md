# File Research: sources/os/linux/linux/fs/nfsd/nfssvc.c

## Summary
Provides the central NFSD service engine: RPC program/version registration, server creation and destruction, per-net startup/shutdown, thread management, write verifier generation, address notifiers, RPC request initialization, the nfsd kernel thread loop, and duplicate reply cache dispatch integration.

## Main Responsibilities
- Defines `nfsd_programs[]` for NFS, optional NFSACL, and optional LOCALIO RPC programs.
- Maintains enabled protocol versions and minor versions per net namespace.
- Creates and binds `svc_serv` instances, registers address notifiers, starts/stops lockd and NFSD per-net resources, and tears them down.
- Implements global and per-net startup/shutdown for NFSv4 state, file cache, duplicate reply cache, lockd, and export flushing.
- Manages thread counts across pools with maximum enforcement and dynamic thread growth/shrink.
- Generates and copies the stable write verifier used by WRITE/COMMIT semantics.
- Dispatches decoded RPCs through the duplicate reply cache and procedure encode/decode paths.

## Key Data Structures and Interfaces
- `nfsd_mutex` serializes `nn->nfsd_serv`, listener lists, service setup, and mutable startup settings.
- `nfsd_programs[]` ties program numbers to version tables, authentication, request initialization, and rpcbind registration.
- `nfsd_version[]`, optional `nfsd_acl_version[]`, and optional `localio_versions[]` form protocol version tables.
- `nfsd_net_ref` protects per-net NFSD state during active service operation.
- `nfsd()` is the service kthread entry point.
- `nfsd_dispatch()` is the shared dispatcher for NFS, NFSACL, and LOCALIO procedure tables.

## Important Behavior
`nfsd_create_serv()` initializes per-net refs, default block size, enabled versions, a pooled SunRPC service, rpcbind binding, address notifiers, and a new write verifier. It leaves `nn->nfsd_serv` visible under notifier lock only after successful bind.

`nfsd_startup_net()` requires at least one configured permanent listener, starts lockd when NFSv2/v3 are enabled, starts per-net file cache and reply cache, then starts NFSv4 state. Failure unwinds in reverse order.

`nfsd_set_nrthreads()` caps total threads to `NFSD_MAXSERVS` and scales excessive per-pool requests down. A single thread-count value is treated specially as an even distribution request across pools with `min_threads`.

The `nfsd` kthread loop waits in `svc_recv()`, disposes deferred filecache items, kills excess dynamic threads after idle timeout, and spawns more threads when all are busy and the pool is below its maximum.

`nfsd_dispatch()` decodes arguments, marks request fields stable through `rq_status_counter`, consults the duplicate reply cache, executes the procedure, encodes the result, marks request fields unstable again, and updates or bypasses the cache according to procedure policy and drop/error outcomes.

Address notifiers age temporary transports immediately when IPv4/IPv6 addresses go down, preventing stale connection state from lingering against removed local addresses.

## Dependencies
Depends on SunRPC service, pooling, stats, transports, rpcbind, duplicate reply cache, NFSD VFS/filecache/state/export helpers, lockd, NFSACL, LOCALIO, network address notifiers, IPv6 optional support, freezer/kthread APIs, siphash, and tracepoints.

## Risks and Subtleties
`nfsd_mutex` is the main correctness boundary. Server pointer publication, listener mutation, version changes, dynamic thread changes, and destruction must remain serialized.

The request status counter protocol is used by netlink RPC-status readers; any dispatcher changes must preserve odd/even release/acquire semantics around stable request fields.

Startup requires configured listeners before threads start. Control paths that create `svc_serv` without threads must destroy it if no listeners or threads remain, or they can leave unusable service state.

The NFSACL mismatch helpers appear to test support using the requested version inside loops, which is a subtle area to treat carefully if modifying version-negotiation behavior.
