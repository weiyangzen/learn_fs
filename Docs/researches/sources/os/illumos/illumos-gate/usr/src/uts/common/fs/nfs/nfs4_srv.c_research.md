# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_srv.c

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-10241, source bytes 262093, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_nfs_nfs4_srv_c_1_1_aaf06cf9ec1f_research.md`
- chunk 2: lines 10242-10676, source bytes 10556, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_nfs_nfs4_srv_c_2_1_f573cab820d6_research.md`

## Chunk Research

### Chunk 1: lines 1-10241

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_srv.c lines 1-10241

## Scope

This chunk covers the first 10,241 lines of `nfs4_srv.c`, the bulk of the illumos in-kernel NFSv4 server operation implementation. It includes server/zone initialization, the NFSv4/v4.1/v4.2 operation dispatch table, compound request execution, filehandle navigation, SECINFO, attribute conversion, namespace mutations, read/write I/O, open/share/delegation state, clientid setup, close, byte-range locking, share locks, RDMA read reply setup, and the start of referral/reparse helpers. The file continues after this chunk with referral path construction and failover helpers.

## APIs And Entry Points

- Server lifecycle: `nfs4_get_srv()`, `rfs4_srv_zone_init()`, `rfs4_srv_zone_fini()`, `rfs4_srvrinit()`, `rfs4_srvrfini()`, `rfs4_do_server_start()`.
- Compound state lifecycle: `rfs4_init_compound_state()`, `rfs4_fini_compound_state()`.
- Grace/server-instance management: `rfs4_grace_start()`, `rfs4_servinst_grace_new()`, `rfs4_servinst_in_grace()`, `rfs4_clnt_in_grace()`, `rfs4_grace_reset_all()`, `rfs4_grace_start_new()`, `rfs4_servinst_create()`, `rfs4_servinst_destroy_all()`, `rfs4_servinst_assign()`, `rfs4_servinst()`.
- NFSv4 operation handlers in this chunk: ACCESS, CLOSE, COMMIT, CREATE, DELEGPURGE, DELEGRETURN, GETATTR, GETFH, LINK, LOCK, LOCKT, LOCKU, LOOKUP, LOOKUPP, OPENATTR, NVERIFY, OPEN, OPEN_CONFIRM, OPEN_DOWNGRADE, PUTFH, PUTPUBFH, PUTROOTFH, READ, READDIR free path, READLINK, RELEASE_LOCKOWNER, REMOVE, RENAME, RENEW, RESTOREFH, SAVEFH, SECINFO, SETATTR, SETCLIENTID, SETCLIENTID_CONFIRM, VERIFY, WRITE.
- NFSv4.1 symbols declared and dispatched here but implemented elsewhere include `rfs4x_op_exchange_id()`, `rfs4x_op_create_session()`, `rfs4x_op_destroy_session()`, `rfs4x_op_sequence()`, `rfs4x_op_reclaim_complete()`, `rfs4x_op_destroy_clientid()`, `rfs4x_op_bind_conn_to_session()`, `rfs4x_op_secinfo_noname()`, `rfs4x_op_free_stateid()`, `rfs4x_op_backchannel_ctl()`, and `rfs4x_op_test_stateid()`.
- Main dispatcher/free/idempotency APIs: `rfs4_compound()`, `rfs4_compound_free()`, `rfs4_idempotent_req()`.
- Lock/share support exported to state teardown: `rfs4_client_sysid()`, `rfs4_release_share_lock_state()`, `rfs4_share()`, `rfs4_unshare()`.
- Referral/reparse helper boundary begins at `rdma_setup_read_data4()` and `vn_find_nfs_record()`; `vn_find_nfs_record()` starts at line 10241 and continues in the next chunk.

## Dispatch And Control Flow

`rfsv4disptab` is the central opcode table. Each entry binds an NFS op number to a handler, a result-free callback, and flags such as `OP_IDEMPOTENT` and `OP_CLEAR_STATEID`. NFSv4.1 session and pNFS-related opcodes are present in the same table; unsupported v4.1/v4.2 operations route to `rfs4_op_notsup()`. `rfs4_opnum_in_range()` enforces minor-version-specific opcode ceilings before dispatch.

`rfs4_compound()` copies the request tag, obtains RPC credentials and NFS security flavor through `sec_svc_getcred()`, allocates one result slot per requested op, records request metadata in `compound_state_t`, and runs the compound under `nfs_export_t.exported_lock`. On the first compound after startup it starts any new server-instance grace periods. For each op, it updates per-op kstats, calls the dispatch handler, stops on first non-`NFS4_OK`, shrinks the result array when execution stops early, and clears the current stateid when the operation table requests it. `rfs4_compound_free()` walks the returned ops and invokes the table free callbacks.

Most operation handlers follow the same guard pattern: verify current/saved filehandle presence, check object type, check export access (`cs->access`), validate UTF-8 component names, convert names through `nfscmd_convname()`, enforce `rdonly4()`, call VFS/VOP primitives, map errno through `puterrno4()`, update `*cs->statusp`, and emit DTrace start/done probes.

## Server State And Stable Storage

`rfs4_srv_zone_init()` allocates one `nfs4_srv_t` per zone, builds a write verifier from hostid/time or high-resolution time, initializes delegation/state/server-instance locks, and defaults delegation policy to `SRV_NEVER_DELEGATE`. Global server init creates delegation FEM templates, allocates a lock-test sysid, creates vnode-specific data storage, and initializes global NFSv4 state.

Cold `rfs4_do_server_start()` initializes state databases and duplicate-request cache, reads stable storage paths when configured in the global zone, sets the maximum minor version, and optionally enables delegation. Warm start reuses existing NFSv4 state and calls `hanfsv4_failover()` on clustered failover; that helper is declared here and implemented after this chunk.

Server instances model grace periods and durable stable-storage paths. `rfs4_servinst_create()` builds a new current instance, creates a dummy oldstate list node for `insque/remque`, records per-path `rfs4_dss_path_t` entries, and can start grace. Clients point at a server instance via `rfs4_servinst_assign()`. `rfs4_servinst_destroy_all()` tears down all instance/path allocations.

## Namespace, Filehandles, And Security

`PUTROOTFH`, `PUTPUBFH`, and `PUTFH` establish `cs->vp`, `cs->fh`, `cs->exi`, and request credentials. They reset old vnodes/creds, validate exports with `checkexport4()`, translate handles with `nfs4_fhtovp()`, and call `call_checkauth4()` to enforce export security and UID mapping. `call_checkauth4()` first checks whether the RPC security flavor matches the export namespace or `AUTH_NONE`, then delegates detailed auth to `checkauth4()`.

`do_rfs4_op_lookup()` handles normal lookup, dot-dot traversal, mount traversal, LOFS boundary detection, pseudo-export visibility, export transitions, label checks, and filehandle construction. It may replace `cs->vp` and `cs->exi`, reset credentials to `basecr`, and rerun export auth after crossing into another export. `LOOKUPP` delegates to the same helper with `".."` and deliberately converts `NFS4ERR_WRONGSEC` to success as required by the NFSv4 LOOKUPP rule in the local comment.

`SECINFO` computes security flavors for a named child. It supports dot-dot, pseudo exports, limited visibility, mounted-on fallback, and RPCSEC_GSS mechanism/QOP/service result construction. `SECINFO` in session mode consumes the current filehandle on success. Result memory for GSS OIDs and arrays is released by `rfs4_op_secinfo_free()`.

Trusted Extensions label checks appear in ACCESS, LOOKUP, PUTPUBFH, REMOVE, RENAME, SETATTR, and CREATE/OPEN create paths. Admin-low clients receive special treatment, including trusted host checks in LOOKUP.

## Attribute Path

The chunk defines `struct nfs4_ntov_table` and helpers for translating between NFSv4 attribute bitmaps and vnode/statvfs attributes:

- `bitmap4_to_attrmask()` maps requested fattr bits to `vattr.va_mask`, determines whether `VFS_STATVFS()` is needed, tracks named-attribute filehandle flags, and handles `rdattr_error`.
- `bitmap4_get_sysattrs()` obtains statvfs and vnode attributes.
- `do_rfs4_op_getattr()` uses `nfs4_ntov_map` conversion callbacks to collect supported attributes, performs optional per-entry `rdattr_error` handling for READDIR-style callers, asks a write delegation holder for authoritative CHANGE/SIZE through `rfs4_cb_getattr()`, XDR-encodes the returned attribute list, and frees conversion state.
- `do_rfs4_set_attrs()`, `decode_fattr4_attr()`, `rfs4_verify_attr()`, and `do_rfs4_op_setattr()` decode incoming fattr4 blobs for SETATTR/VERIFY/NVERIFY/CREATE/OPEN create, delay ACL setting until after mode changes, handle size changes through stateid checks and `VOP_SPACE()`, enforce NBMAND lock conflicts, and build response attr bitmaps.

GETATTR also detects NFS referral reparse points with `vn_is_nfs_reparse()`. Older Solaris v4 clients are shown referrals as symlinks via `client_is_downrev()`; newer clients get referral metadata. Those helpers are implemented after this chunk.

## File And Directory Operations

CREATE is limited to non-regular objects; regular file creation is handled by OPEN. It validates object type, names, read-only exports, labels, and attributes, then calls `VOP_MKDIR()`, `VOP_SYMLINK()`, or `VOP_CREATE()` for special files. It records directory change info from ctime and `va_seq`, fsyncs parent/object metadata, constructs a new filehandle, and updates `cs->vp`.

LINK, REMOVE, and RENAME all compute before/after change_info, validate cross-export boundaries, recall conflicting delegations, check NBMAND conflicts, call the relevant VOP (`VOP_LINK`, `VOP_REMOVE`/`VOP_RMDIR`, `VOP_RENAME`), fsync metadata, and determine `cinfo.atomic` from `va_seq`. REMOVE and RENAME close all NFSv4 state when the affected file’s link count reaches zero. RENAME also updates vnode path cache with `vn_renamepath()` and has optional volatile filehandle test support.

OPENATTR opens/creates extended-attribute directories via `VOP_LOOKUP(..., LOOKUP_XATTR | CREATE_XATTR_DIR)` when allowed, verifies named-attribute access using ACE-aware access checks when available, and marks the filehandle with `FH4_ATTRDIR`.

READLINK handles normal symlinks and downrev-client referral symlink emulation. It reads a symlink with `VOP_READLINK()` or asks `build_symlink()` for a synthetic referral string, then converts outbound naming and UTF-8 encodes the reply.

## Read/Write And RDMA

`do_io()` wraps `VOP_READ()`/`VOP_WRITE()` with vnode rwlocks, nonblocking mandatory-lock behavior, and short exponential retry on `EAGAIN`. READ and WRITE both call `rfs4_check_stateid()` to validate open/delegation state, then enforce regular-file type, access, mandatory locking, read-only exports, and NBMAND conflicts.

READ supports three data paths: RDMA write chunks from `args->wlist`, loaned zero-copy TCP buffers via `VOP_REQZCBUF()`/`uio_to_mblk()`, and normal mblk allocation from `rfs_read_alloc()`. It clamps count to `rfs4_tsize(req)`, handles EOF/zero-length fast paths, fills `READ4res` data pointers/mblk/wlist, and uses `rdma_setup_read_data4()` to prepare RDMA chunk lengths. `rfs4_op_read_free()` releases mblk-backed read replies.

WRITE accepts data from mblks, RDMA read chunks, or inline buffers, converts mblks to iovecs, applies process file-size limit, chooses sync semantics from `UNSTABLE4`, `FILE_SYNC4`, or `DATA_SYNC4`, temporarily sets `curthread->t_cred` for quota behavior during VM faults, calls `do_io(FWRITE)`, and returns count/commit mode/write verifier.

## OPEN, Delegations, And Share State

The OPEN path is the largest state machine in the chunk. Helpers include `rfs4_lookup()`, `rfs4_lookupfile()`, `create_vnode()`, `check_open_access()`, `rfs4_verifier_to_mtime()`, `rfs4_createfile()`, `rfs4_do_open()`, and claim-specific wrappers for `CLAIM_NULL`, `CLAIM_PREVIOUS`, `CLAIM_DELEGATE_CUR`, `CLAIM_DELEGATE_PREV`, and `CLAIM_FH`.

`rfs4_op_open()` validates/normalizes clientid, enforces v4.1 session clientid semantics, handles lease expiration, grace/reclaim rules, open-owner lookup, v4.0 seqid replay, open-owner confirmation, share access/deny validation, mountpoint denial, and claim dispatch. On success or replay it updates lease, cached open response/filehandle, open seqid, current stateid, and confirmation flags.

`rfs4_do_open()` creates or finds `rfs4_file_t` and `rfs4_state_t`, allocates a client sysid, acquires share locks with `rfs4_share()`, retries once after cleaning recently expired state on share denial, recalls conflicting delegations, opens or upgrades the vnode, updates per-file share/access counters, grants or explains delegations, records v4.1 recalled-state tracking through `rfs4x_rs_record()`, bumps stateid sequence, and releases state/file references.

`rfs4_createfile()` covers OPEN create modes. It decodes create attrs, handles EXCLUSIVE4/EXCLUSIVE4_1 verifiers through mtime, creates or looks up regular files, supports duplicate exclusive create detection by verifier mtime, builds change_info, fsyncs directory/object metadata, handles truncation of pre-existing files with delegation recall/NBMAND checks, builds the filehandle, and updates `cs->vp`.

OPEN_CONFIRM, OPEN_DOWNGRADE, and CLOSE all validate filehandle/stateid ownership, serialize on the open-owner sequence wrapper, handle replay/error sequencing for v4.0, update stateids and cached replies, and release/downgrade vnode/share state. `rfs4_release_share_lock_state()` is the teardown hook that removes per-client locks, cleans per-lockowner locks, unshares, updates per-file counters, and calls `VOP_CLOSE()`.

## Clientid And Callback State

`rfs4_op_setclientid()` implements the RFC-described v4.0 clientid state machine. It records the caller address, tracks old Solaris clients lacking referral support by client IP, finds or creates unconfirmed clients, handles lease-expired confirmed clients by closing and retrying, returns `NFS4ERR_CLID_INUSE` with callback location on credential mismatch, updates callback info when verifier matches, replaces stale unconfirmed records, and hides an existing confirmed record while creating a replacement unconfirmed one.

`rfs4_op_setclientid_confirm()` validates clientid and confirm verifier, marks the client confirmed as v4.0, closes the displaced confirmed client if present, assigns the current server instance, records the clientid in stable storage (`rfs4_ss_clid()`), starts callback-path checking, updates the lease, and checks whether stable storage allows reclaim (`rfs4_ss_chkclid()`).

`rfs4_op_renew()` refreshes a client lease and returns `NFS4ERR_CB_PATH_DOWN` once when callback path-down notification has not yet been delivered.

## Locking

The byte-range locking stack maps NFSv4 lock owners/stateids to illumos `VOP_FRLOCK()` calls:

- `rfs4_client_sysid()` lazily allocates an LM sysid for a client.
- `setlock()` performs nonblocking lock attempts with retry/backoff and resolves denied-lock ownership with `F_GETLK`, including a bounded retry for a race where the conflicting lock disappears before it can be reported.
- `rfs4_do_lock()` validates open modes, maps NFS lock ranges and lock types to POSIX `flock64`, temporarily releases state locks around filesystem locking, cleans newly acquired locks if the open state closed concurrently, bumps lock stateid on success, and maps VOP errors to NFSv4 lock statuses.
- `rfs4_op_lock()` handles both new and existing lock-owner branches, open-stateid and lock-stateid validation, v4.0 seqid replay, v4.1 session behavior, grace/reclaim rules, duplicate new-lock-owner handling, and reply caching.
- `rfs4_op_locku()` validates lock state and seqid, blocks unlock during grace, then calls `rfs4_do_lock()` with unlock semantics.
- `rfs4_op_lockt()` is best-effort test locking. It validates clientid/lease/grace, ignores client-supplied owner clientid under sessions, finds or fabricates owner identity, calls `F_GETLK`, and returns `LOCK4denied` data.
- `lock_denied()` allocates denied-owner data from known NFSv4 lockowners or fabricates it from sysid/pid. `lock_denied_free()` releases that owner buffer for LOCK/LOCKT replies.

Share reservation support is separate from byte-range locking. `rfs4_share()` maps NFS share access/deny to `VOP_SHRLOCK(F_SHARE[_NBMAND])`, updates state share masks, and returns `NFS4ERR_SHARE_DENIED` on `EAGAIN`. `rfs4_unshare()` removes the reservation with `F_UNSHARE`.

## Dependencies

This chunk is tightly coupled to illumos kernel VFS/vnode APIs (`VOP_LOOKUP`, `VOP_CREATE`, `VOP_OPEN`, `VOP_CLOSE`, `VOP_GETATTR`, `VOP_SETATTR`, `VOP_ACCESS`, `VOP_READ`, `VOP_WRITE`, `VOP_FSYNC`, `VOP_FRLOCK`, `VOP_SHRLOCK`, `VFS_STATVFS`, `traverse`, `untraverse`, `makefh4`, `nfs4_fhtovp`), NFS export/auth logic (`checkexport4`, `nfs_visible`, `nfs_exported`, `nfs_vptoexi`, `checkauth4`, `nfsauth4_secinfo_access`, `rdonly4`), NFSv4 state databases/delegation code (`rfs4_findclient*`, `rfs4_findopenowner`, `rfs4_findstate*`, `rfs4_findfile*`, `rfs4_check_stateid*`, `rfs4_grant_delegation`, `rfs4_recall_deleg`, `rfs4_return_deleg`, `rfs4_update_*`), stable-storage helpers (`rfs4_dss_*`, `rfs4_ss_*`), RPC/RDMA helpers (`svc_getrpccaller`, `sec_svc_getcred`, `rdma_get_wchunk`, `rdma_setup_read_chunks`), STREAMS mblk helpers, FEM delegation monitors, NBMAND locks, Trusted Extensions labels, and XDR conversion routines in `nfs4_ntov_map`.

## Risks And Review Notes

- The compound dispatcher holds `exported_lock` across all operations in a compound, while many operations can block on VFS, delegation callbacks, I/O, or locks. The comment says this is a namespace redesign tradeoff; it is a scalability and deadlock-sensitive area.
- Many handlers manually manage vnode holds/releases, credential replacement, allocated names, XDR blobs, mblks, and state DB references. Error exits are intricate, especially CREATE, REMOVE, RENAME, OPEN, and LOCK.
- OPEN/CLOSE/LOCK replay semantics depend on exact v4.0 seqid handling and cached replies. Any change to status ordering can break client retransmission behavior.
- Share/open state counters in `rfs4_do_open()`, `rfs4_op_open_downgrade()`, and `rfs4_release_share_lock_state()` must stay consistent with VOP open/close/downgrade calls. A suspicious line in OPEN_DOWNGRADE clears `fp->rf_share_deny` with `~OPEN4_SHARE_ACCESS_WRITE` when write access count reaches zero; that looks like it may intend `rf_share_access`, but this report only records the observed code.
- RENAME’s target after-change getattr uses `VOP_GETATTR(odvp, &nadva, ...)` rather than `ndvp`; if source and target directories differ, this may affect target `change_info`. This is another observed risk, not a patch.
- Attribute handling trusts `nfs4_ntov_map` callback behavior heavily. Delayed ACL setting, partial SETATTR success bitmaps, and createattr verification policy are intentionally best-effort and can surprise protocol clients.
- Delegation recall paths deliberately drop locks and retry, so state may close or change concurrently. The code handles several races, but these areas are high-risk.
- Lock denial reporting has unavoidable races with POSIX locks; `setlock()` bounds retries at 10 and may lose precise denied-owner information under heavy churn.
- Referral support is split across chunks. This chunk calls `vn_is_nfs_reparse()`, `client_is_downrev()`, `build_symlink()`, and starts `vn_find_nfs_record()` at line 10241; their implementations and failover helper are in the next chunk.

## Cross-Chunk References

- `vn_find_nfs_record()` begins at the final line of this chunk and continues after line 10241. It likely supports `vn_is_nfs_reparse()`, `fetch_referral()`, and `build_symlink()`.
- Referral/reparse helpers used earlier but implemented after this chunk: `vn_is_nfs_reparse()`, `nfs4_create_components()`, `make_pathname4()`, `fetch_referral()`, `build_symlink()`, `client_is_downrev()`.
- `hanfsv4_failover()` is declared and called in `rfs4_do_server_start()` for clustered warm starts, but its implementation is after this chunk.
- NFSv4.1 session operations and several callback/delegation helpers are declared or called here but implemented in sibling NFSv4 server/state files, not in this chunk.

### Chunk 2: lines 10242-10676

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_srv.c lines 10242-10676

## Scope

This report covers `sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_srv.c` lines 10242-10676 for subset A (`Docs/research_subset_a.md`). The chunk contains NFS referral support built on Solaris/illumos reparse points, compatibility handling for clients that cannot consume NFSv4 referrals, and the HA-NFSv4 resource-group failover reconciliation helper. Adjacent context shows the referral disable tunable `rfs4_no_referrals` immediately before the chunk and server-start failover callers earlier in the same file.

## Public And Internal APIs Covered

- `vn_find_nfs_record(vnode_t *vp, nvlist_t **nvlp, char **svcp, char **datap)` parses vnode reparse data into an `nvlist_t`, finds the first nvpair whose name begins with `NFS` case-insensitively, returns the service type and string data, and transfers ownership of the nvlist to the caller on success.
- `vn_is_nfs_reparse(vnode_t *vp, cred_t *cr)` is the boolean gate used by server paths to decide whether a vnode is an NFS referral point. It honors `rfs4_no_referrals`, verifies `vn_is_reparse()`, then probes for an NFS reparse record.
- `nfs4_create_components(char *path, component4 *comp4)` splits a path on `/`, NUL, or newline and optionally converts components to NFSv4 UTF-8. Comments require it to stay in sync with user-level `ref_subr.c`.
- `make_pathname4(char *path, pathname4 *pathname)` counts components, allocates a `component4` array, fills a `pathname4`, and returns the component count.
- `fetch_referral(vnode_t *vp, cred_t *cr)` resolves an NFS reparse point into an allocated `fs_locations4` by upcalling `reparse_kderef()`, decoding XDR `fattr4_fs_locations`, and setting `fs_root` from `vp->v_path`.
- `build_symlink(vnode_t *vp, cred_t *cr, size_t *strsz)` converts the first referral location and first server into a legacy `/net/<server>/<rootpath...>` symlink target.
- `client_is_downrev(struct svc_req *req)` maps an RPC caller address to `rfs4_clntip_t` and returns `ri_no_referrals`.
- `hanfsv4_failover(nfs4_srv_t *nsrv4)` reconciles current DSS paths with new `nfsd` resource-group paths, removes paths no longer served, creates a server instance for added paths, reads stable state, and resets grace periods.

## Control Flow And Behavior

- Referral detection checks `rfs4_no_referrals`, `vn_is_reparse()`, then `vn_find_nfs_record()`. Successful `vn_find_nfs_record()` callers own the returned nvlist and must call `reparse_free(nvl)`.
- Path conversion is two-pass: count non-empty components, allocate `component4[]`, then populate it. Empty components from repeated/leading slashes are skipped; newline terminates parsing.
- `fetch_referral()` uses a fixed 1024-byte stack buffer for `reparse_kderef()`, then decodes the daemon response with `xdr_fattr4_fs_locations`.
- `build_symlink()` only consumes `locations_val[0]` and `server_val[0]`, appends convertible rootpath components, frees the decoded referral, and returns the allocated symlink buffer.
- `client_is_downrev()` does not create missing client-IP records; absent state means “not downrev.”
- `hanfsv4_failover()` first removes missing paths from circular `nsrv4->dss_pathlist`, skipping `NFS4_DSS_VAR_DIR`. It then builds an `added_paths` array from unmatched `rfs4_dss_newpaths`, creates a new server instance if needed, reads DSS state, and restarts active grace periods.

## State And Data Structures

- Reparse state is an `nvlist_t`; returned `stype` and `sdata` point into that nvlist lifetime.
- Referral payloads use `fs_locations4`, `fs_location4`, `pathname4`, `component4`, and UTF-8 protocol wrappers. Nested memory is released by `rfs4_free_fs_locations4()`.
- Symlink compatibility uses transient `utf8_to_str()` buffers and a returned `kmem_zalloc()` string. `strsz` is the allocation size.
- HA state is held in `nfs4_srv_t::dss_pathlist`, circular `rfs4_dss_path_t` nodes, and each `rfs4_servinst_t::dss_paths`.
- New HA input comes from global `rfs4_dss_newpaths` / `rfs4_dss_numnewpaths`, assumed sorted and duplicate-free by `nfsd`.

## Dependencies

- VFS/reparse: `vn_is_reparse()`, `reparse_init()`, `reparse_vnode_parse()`, `reparse_free()`, nvlist/nvpair APIs, and `reparse_kderef()`.
- XDR/protocol: `xdrmem_create()`, `xdr_fattr4_fs_locations()`, `XDR_DESTROY()`, `str_to_utf8()`, `utf8_to_str()`.
- RPC/client state: `svc_getrpccaller()`, `rfs4_find_clntip()`, `rfs4_dbe_rele()`.
- HA-NFSv4: `NFS4_DSS_VAR_DIR`, `rfs4_servinst_create()`, `rfs4_dss_readstate()`, `rfs4_grace_reset_all()`, `insque()`/`remque()`.
- Cross-file consumers include NFSv2/v3 lookup/readlink paths, NFSv4 compound/readdir paths, and NFSv4 `fs_locations` attribute generation.

## Risks And Invariants

- `fetch_referral()` appears to leak the allocated `fs_locations4` wrapper if XDR decoding fails after `kmem_alloc()`.
- `fetch_referral()` frees the reparse nvlist before its DTrace probe references `stype` and `sdata`; those pointers are nvlist-owned.
- The 1024-byte referral buffer may fail for large referral payloads.
- `nfs4_create_components()` copies into `char buf[MAXNAMELEN]` without checking `slen < MAXNAMELEN`.
- `build_symlink()` assumes at least one location and one server in decoded data.
- `build_symlink()` sizes the destination from UTF-8 recorded lengths but concatenates converted strings, making length semantics important.
- `hanfsv4_failover()` assumes `dss_pathlist` is non-NULL and circular because `NFS4_DSS_VAR_DIR` is always present.
- Removal mutates the circular list while walking it; correctness depends on the default path never being removed and list invariants staying intact.
- Addition detection uses prefix comparison, unlike exact comparison for removals.
- The failover algorithm is documented as roughly `2 * O(n**2)` and has no visible local locking; it relies on higher-level server-start/reconfiguration serialization.

## Cross-Chunk References

- Earlier same-file `rfs4_do_server_start()` calls `hanfsv4_failover()` on warm clustered start; cold start reads `rfs4_dss_newpaths` directly.
- Earlier same-file helpers define `rfs4_grace_reset_all()`, `rfs4_dss_newpath()`, and `rfs4_servinst_create()`.
- Earlier NFSv4 compound paths use `vn_is_nfs_reparse()`, `client_is_downrev()`, and `build_symlink()` to choose moved/referral versus symlink compatibility behavior.
- `nfs4_srv_attr.c` calls `fetch_referral()` for `FATTR4_FS_LOCATIONS` and defines `rfs4_free_fs_locations4()`.
- `nfs4_srv_readdir.c` uses referral helpers while walking directories and encoding `fs_locations`.
- NFSv2/v3 server files also call `vn_is_nfs_reparse()` and `build_symlink()`, so these helpers serve legacy protocol compatibility as well as NFSv4.
