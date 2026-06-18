# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_server.c

## Purpose

`nfs_server.c` is the illumos NFS server module front door. It handles module initialization, per-zone server globals, `nfs_svc()` transport registration, RDMA listener startup, NFSv4 server start/stop/quiesce coordination, central RPC dispatch for NFS and NFS_ACL programs, authentication and credential mapping, logging hook integration, public filehandle multicomponent lookup, Trusted Extensions label checks, and zero-copy read buffer helpers.

The actual NFSv2/v3 operation bodies live in other files, but this file decides how requests enter those operations and how replies, duplicate request caching, authorization, and logging are handled.

## Module and Global State

`_init()` calls `nfs_srvinit()`, installs the module, registers function pointers used by `nfssys()` for server quiesce and NFSv4 DSS path setup, initializes DSS path globals, and creates the `nfs_xuio_cache` used by zero-copy read support. `_fini()` returns `EBUSY`, so the server module is not unloadable during normal operation.

Global state includes:

- `nfssrv_zone_key` for per-zone `nfs_globals_t`.
- `nfssrv_globals_list` and `nfssrv_globals_rwl` for visibility across zones.
- `nfs_xuio_cache` and `nfs_loaned_buffers` for copy-reduction paths.
- NFSv4 distributed stable storage globals: `rfs4_dss_newpaths`, `rfs4_dss_numnewpaths`, `rfs4_dss_paths`, and `rfs4_dss_oldpaths`.
- Server callout tables for CLTS, COTS, and RDMA transports.

`nfs_srv_getzg()` caches the current zone's server globals in thread-specific data to reduce repeated `zone_getspecific()` lookups.

## Server Startup and Shutdown

`nfs_svc()` is the system-call path used by `nfsd` to register a transport. It validates the file descriptor, initializes the root export filehandle, computes a read buffer size, copies netid and address mask from userspace, records version min/max, selects a transport-specific service callout table, starts the NFSv4 server if the max version is v4, creates a kernel TLI service transport with `svc_tli_kcreate()`, releases the file descriptor, and records the cluster node ID for HA lock-manager state when clustered.

`rfs4_server_start()` serializes NFSv4 server startup with `nfs_server_upordown_lock`. It waits for old stop/offline transitions to finish, registers service pool offline/shutdown callbacks, calls `rfs4_do_server_start()`, and moves state to `NFS_SERVER_RUNNING`.

`nfs_srv_offline()`, `nfs_srv_stop_all()`, `nfs_srv_quiesce_all()`, and `nfs_srv_shutdown_all()` coordinate service-pool offline, full stop, and quiesce. Quiesce preserves NFSv4 state for warm start. Full stop finalizes NFSv4 state and duplicate reply cache state before marking the server stopped.

`rdma_start()` configures RDMA callout versions, starts NFSv4 if needed, creates RDMA transports, waits for RDMA attach/detach/interruption events, and restarts or stops RDMA services accordingly.

## Dispatch Tables

The file defines dispatch tables for:

- NFSv2: procedures 0-17, including ordinary file/namespace operations and unsupported ROOT/WRITECACHE stubs.
- NFSv3: procedures 0-21, including COMMIT and READDIRPLUS.
- NFSv4: NULL and COMPOUND.
- NFS_ACL v2 and v3 procedures.

Each `rpcdisp` entry contains:

- operation function
- normal and fast XDR arg decoders
- arg structure size
- normal and fast XDR result encoders
- result structure size
- result-free function
- dispatch flags
- filehandle extractor

Important flags include `RPC_IDEMPOTENT`, `RPC_ALLOWANON`, `RPC_MAPRESP`, `RPC_PUBLICFH_OK`, and `RPC_AVOIDWORK`.

Large `union rfs_args`, `union rfs_res`, `union acl_args`, and `union acl_res` provide stack storage for all supported argument/result structures.

## Common Dispatch Flow

`common_dispatch()` is the central request engine for NFSv2, NFSv3, and ACL requests.

The flow is:

1. Validate RPC version and procedure against the selected program dispatch table.
2. Increment per-procedure kstats.
3. Decode arguments using fast XDR when allowed and available, otherwise normal XDR.
4. For NFSv4, delegate to `rfs4_dispatch()` after decode.
5. Extract the filehandle when the operation has one.
6. Compute `anon_ok` for exported-root getattr/statfs-style access using equal object/export fids.
7. Resolve `exportinfo_t` with `checkexport()`.
8. Reject pseudo exports for non-v4 clients.
9. Run `checkauth()` to validate flavor/access and map credentials.
10. Allocate result storage, sometimes from transport response buffers when `RPC_MAPRESP` allows fast reply encoding.
11. For non-idempotent operations, consult the duplicate request cache via `SVC_DUP_EXT()`.
12. Call the operation body, with `T_DONTPEND` set to control asynchronous blocking behavior.
13. Finalize duplicate request cache state through `SVC_DUPDONE_EXT()`.
14. Convert operation-level wrong-security responses into `svcerr_weakauth()`.
15. If NFS logging is active, choose a logging export and copy remote netbuf/result data before reply buffers can be freed.
16. Send the reply using fast result XDR when possible.
17. Write the NFS log record after reply send.
18. Free operation-specific result data if not held by duplicate cache.
19. Free decoded args, release export references, and update bad-call/total-call kstats.

This dispatcher is the main point where RPC mechanics, export lookup, auth, duplicate suppression, logging, and operation execution meet.

## Authentication and Credential Mapping

`checkauth()` handles NFSv2/v3 and ACL request authorization. It enforces optional privileged-port checks, obtains RPC credentials with `sec_svc_getcred()`, allows public-filehandle operations after credential setup, asks `nfsauth_access()` for export policy decisions, and maps credentials according to the selected flavor and export policy.

Behavior includes:

- `NFSAUTH_DROP` silently drops the request.
- `NFSAUTH_RO` marks the request read-only for operation handlers.
- `NFSAUTH_DENIED` usually weak-auth fails, except some anonymous mount-related access can map to AUTH_NONE.
- `NFSAUTH_MAPNONE` maps credentials to anonymous because AUTH_NONE was allowed.
- `NFSAUTH_WRONGSEC` is denied for v2/v3.
- AUTH_NONE maps to `ex_anon`.
- AUTH_UNIX root maps to anonymous unless root access or UID mapping permits otherwise.
- AUTH_UNIX with UID/GID mapping updates the request credential and optional group list.
- AUTH_DES and RPCSEC_GSS validate auth window, check root principal lists, map allowed root principals to `s_rootid`, and map unlisted root/nobody principals to anonymous.

`checkauth4()` is the NFSv4 equivalent working from `compound_state`. It uses `nfsauth4_access()`, returns `-2` for wrong security flavor so NFSv4 can produce protocol-level wrongsec behavior, supports limited access via `CS_ACCESS_LIMITED`, and performs similar credential/root/anonymous mapping.

## Public Filehandle Multicomponent Lookup

`rfs_publicfh_mclookup()` evaluates WebNFS/public-filehandle multicomponent lookup paths. It parses the path type with `MCLpath()`:

- printable ASCII means URL path
- `0x80` means native path
- `0x81` means security query, followed by an index byte and another path tag

It resolves the path relative to a starting directory using `rfs_pathname()`, triggers autofs mounts with `VOP_ACCESS()`, traverses mounted filesystems, resolves real vnodes, and checks that the final vnode belongs to an exported filesystem via `nfs_check_vpexi()`. Pseudo exports are rejected for non-v4 public access.

If the export has an index file and the lookup was URL-based into a directory, it tries to resolve the configured index file and may update the export reference accordingly. Security queries set `SEC_QUERY` so filehandle creation can return overloaded security flavor information.

`rfs_pathname()` wraps pathname lookup with zone-root handling, optional URL percent decoding through `URLparse()`, stack-buffer fast path for typical paths, and heap fallback for long paths.

`nfs_check_vpexi()` uses `nfs_vptoexi()` and enforces `EX_NOSUB` by rejecting public lookups that terminate below the exported directory when the export disallows subtree access.

## Zone Lifecycle

`nfs_srvinit()` initializes global server locks/lists/TSD, then initializes export, v2, v3, v4, and auth subsystems in a strict order before creating the zone key.

`nfs_server_zone_init()` allocates `nfs_globals_t`, initializes server start/stop locks and RDMA wait state, records the zone ID, and initializes export, stats, v2/v3/v4 server, and auth per-zone state before linking the globals into `nfssrv_globals_list`.

`nfs_server_zone_shutdown()` calls auth and export shutdown hooks. `nfs_server_zone_fini()` removes the globals from the global list and tears down auth, v4, v3, v2, stats, and export state in reverse order.

`nfs_srvfini()` deletes the zone key, finalizes global submodules in reverse init order, and destroys global TSD/list/lock state. It is primarily used when module install fails because `_fini()` refuses unload.

## Trusted Extensions Label Helpers

`nfs_getflabel()` derives the label for a vnode or, if the vnode has no cached path, the export path. It finds the containing zone by path, holds the zone label, releases the zone, and returns the label.

`do_rfs_label_check()` compares a client label to the server file object's label using equality or dominance, with DTrace instrumentation. These helpers are used by NFSv3 and NFSv4 lookup/access paths.

## Zero-Copy and mblk Helpers

`mblk_to_iov()` converts an mblk chain to an iovec array.

`rfs_setup_xuio()` allocates an `nfs_xuio_t`, initializes a zero-copy xuio wrapper, stores the vnode, sets a reference count, and installs `rfs_free_xuio()` as the external-buffer free callback.

`uio_to_mblk()` wraps uio iovecs in externally stored STREAMS mblks using `esballoca()` and adjusts the xuio reference count to the number of iovecs.

`rfs_free_xuio()` decrements the xuio refcount and only calls `VOP_RETZCBUF()` and releases the vnode when all mblks referencing the loaned buffers have been returned.

`rfs_read_alloc()` allocates mblk chains and corresponding iovecs for read replies, splitting requests into chunks no larger than `kmem_max_cached` to avoid oversized kmem arena costs.

`rfs_rndup_mblks()` sets mblk write pointers to the actual read length and appends XDR padding. For loaned buffers it may allocate an extra padding mblk because loaned buffer sizes are fixed.

## Dependencies and Integration Points

- RPC service transport layer: `svc_tli_kcreate()`, `svc_rdma_kcreate()`, `SVC_GETARGS()`, `svc_sendreply()`, duplicate request cache hooks, service pool callbacks.
- Export management from `nfs_export.c`: `nfs_export_get_rootfh()`, `checkexport()`, `nfs_vptoexi()`, public export state.
- Authorization from `nfs_auth.c`: `nfsauth_access()`, `nfsauth4_access()`, per-zone init/fini/shutdown.
- NFSv2/v3/v4 operation handlers and XDR routines from neighboring server files.
- NFS logging from `nfs_log.c`.
- NFSv4 state, dispatch, and duplicate reply cache: `rfs4_do_server_start()`, `rfs4_dispatch()`, `rfs4_state_zone_fini()`, `rfs4_fini_drc()`.
- VFS/pathname/vnode APIs and STREAMS mblk APIs.
- Cluster/HA and lock-manager state through `clconf_get_nodeid()` and `lm_global_nlmid`.
- Zone infrastructure and Trusted Extensions labels.

## Concurrency and Locking Notes

Server start/stop/quiesce state is protected by `nfs_server_upordown_lock` and coordinated with `nfs_server_upordown_cv`. Per-zone globals are protected globally by `nfssrv_globals_rwl`. Dispatch itself relies on export reference counts returned by `checkexport()`, duplicate request cache synchronization in RPC service code, and operation-specific locking in the called handlers.

The zero-copy path relies on atomic xuio reference counts so external-buffer callbacks return loaned buffers only after every mblk is released.

## Risks and Edge Cases

- `common_dispatch()` is high-risk because it combines decode, auth, duplicate request cache state, logging, reply sending, result freeing, and export reference release.
- Dispatch table entries must stay consistent with operation numbers, XDR functions, result free routines, and `dis_getfh` extractors. A mismatch can cause decode corruption, missing auth checks, or leaks.
- Version callout tables are mutated based on transport and requested min/max; comments note ordering assumptions.
- Public filehandle URL parsing decodes percent escapes in place and treats malformed path tags as `EIO`.
- `checkauth()` has many credential mapping branches; root, anon, UID mapping, AUTH_NONE, RPCSEC_GSS, and root principal lists need regression coverage.
- `nfs_srv_getzg()` caches zone globals in TSD. Correctness depends on calls happening in the intended zone context.
- RDMA restart logic loops on attach/detach events and must stop transports cleanly on service interruption.
- Zero-copy mblk padding differs between copied and loaned buffers; XDR alignment bugs would surface as corrupt read replies.

## Testing and Verification Signals

Useful tests cover NFSv2/v3 dispatch for every procedure, ACL dispatch, NFSv4 compound handoff, bad version/procedure/decode failures, idempotent vs duplicate-cached non-idempotent operations, public filehandle multicomponent lookup and security query paths, AUTH_NONE/AUTH_SYS/AUTH_DES/RPCSEC_GSS credential mapping, read-only export enforcement, wrongsec behavior, NFS logging after reply send, RDMA attach/detach restart, server quiesce vs full stop, zone shutdown/fini ordering, Trusted Extensions label checks, and zero-copy read buffer return/padding behavior.
