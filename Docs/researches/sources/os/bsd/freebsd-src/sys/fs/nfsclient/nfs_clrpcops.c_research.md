# File Research: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_clrpcops.c

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-8651, source bytes 262123, report `Docs/researches/chunks/chunk_sources_os_bsd_freebsd_src_sys_fs_nfsclient_nfs_clrpcops_c_1_1_8651_6f1131018eac_research.md`
- chunk 2: lines 8652-9979, source bytes 39746, report `Docs/researches/chunks/chunk_sources_os_bsd_freebsd_src_sys_fs_nfsclient_nfs_clrpcops_c_2_8652_9979_6867bbc367d5_research.md`

## Chunk Research

### Chunk 1: lines 1-8651

# Chunk Research: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_clrpcops.c lines 1-8651

## Scope

This report covers `sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_clrpcops.c` lines 1-8651 for subset A (`Docs/research_subset_a.md`). The chunk contains the beginning and bulk of the FreeBSD NFS client RPC operation layer for NFSv2, NFSv3, NFSv4.0, NFSv4.1, NFSv4.2, and pNFS client data-server I/O. It spans ordinary vnode-facing RPC wrappers, lower-level XDR builders/parsers, NFSv4 client/open/lock/delegation/session setup, directory enumeration, ACLs, layout/device handling, and pNFS file/flex-file read/write/commit paths. The chunk ends inside `nfsrpc_createlayout()` immediately after emitting the NFSv4 `OPEN` claim type `NFSV4OPEN_CLAIMNULL`; parsing and cleanup for this create+layout compound continue in the next chunk.

## Public And Internal APIs Covered

- Basic RPC entry points: `nfsrpc_null()`, `nfsrpc_access()`, `nfsrpc_accessrpc()`, `nfsrpc_getattr()`, `nfsrpc_getattrnovp()`, `nfsrpc_setattr()`, and the internal `nfsrpc_setattrrpc()`.
- NFSv4 open/close state APIs: `nfsrpc_open()`, `nfsrpc_openrpc()`, `nfsrpc_opendowngrade()`, `nfsrpc_close()`, `nfsrpc_doclose()`, `nfsrpc_closerpc()`, `nfsrpc_openconfirm()`, and `nfsrpc_setclient()`.
- Lookup and namespace APIs: `nfsrpc_lookup()`, `nfsrpc_readlink()`, `nfsrpc_mknod()`, `nfsrpc_create()`, `nfsrpc_createv23()`, `nfsrpc_createv4()`, `nfsrpc_remove()`, `nfsrpc_rename()`, `nfsrpc_link()`, `nfsrpc_symlink()`, `nfsrpc_mkdir()`, `nfsrpc_rmdir()`, and `nfscl_invalidfname()`.
- Data I/O APIs: `nfsrpc_read()`, `nfsrpc_readrpc()`, `nfsrpc_write()`, `nfsrpc_writerpc()`, `nfsrpc_commit()`, `nfsrpc_deallocate()`, `nfsrpc_deallocaterpc()`, `nfsrpc_allocate()`, `nfsrpc_allocaterpc()`, and `nfsrpc_advise()`.
- Directory APIs: `nfsrpc_readdir()` and `nfsrpc_readdirplus()`, including NFSv4 synthetic dot/dotdot generation and optional name-cache population from readdirplus results.
- Locking APIs: `nfsrpc_advlock()`, `nfsrpc_lockt()`, `nfsrpc_locku()`, `nfsrpc_lock()`, and `nfsrpc_rellockown()`.
- Filesystem metadata APIs: `nfsrpc_statfs()`, `nfsrpc_pathconf()`, `nfsrpc_fsinfo()`, `nfsrpc_renew()`, `nfsrpc_getdirpath()`, `nfsrpc_delegreturn()`, `nfsrpc_getacl()`, `nfsrpc_setacl()`, and `nfsrpc_setaclrpc()`.
- NFSv4.1 session/client APIs: `nfsrpc_exchangeid()`, `nfsrpc_createsession()`, `nfsrpc_destroyclient()`, `nfsrpc_reclaimcomplete()`, `nfscl_initsessionslots()`, `nfscl_freenfsclds()`, and `nfscl_getsameserver()`.
- pNFS layout and DS APIs: `nfsrpc_layoutget()`, `nfsrpc_getdeviceinfo()`, `nfsrpc_layoutcommit()`, `nfsrpc_layoutreturn()`, `nfsrpc_layouterror()`, `nfsrpc_getlayout()`, `nfsrpc_fillsa()`, `nfscl_doiods()`, `nfscl_findlayoutforio()`, `nfscl_doflayoutio()`, `nfscl_dofflayoutio()`, `nfsrpc_readds()`, `nfsrpc_writeds()`, `nfsrpc_writedsmir()`, `nfsio_writedsmir()`, `start_writedsmir()`, `nfsrpc_commitds()`, `nfsio_commitds()`, and `start_commitds()`.
- Layout parsing helpers: `nfsrv_setuplayoutget()`, `nfsrv_parselayoutget()`, `nfsrv_parseug()`, `nfsrpc_getopenlayout()`, `nfsrpc_openlayoutrpc()`, and the first half of `nfsrpc_createlayout()`.
- Compile-disabled/not-yet DS advise helpers are present under `#ifdef notyet`: `nfsrpc_adviseds()`, `start_adviseds()`, and `nfsio_adviseds()`.

## Control Flow And Behavior

- Most public vnode-facing routines are wrappers around one or more lower-level RPC builders. For NFSv4 they first acquire a usable stateid via client/open/lock state helpers, perform the RPC, translate recovery-sensitive server errors, release state references, and retry around grace, delay, stale state, old state, bad session, expired client ID, and selected bad stateid cases.
- `nfsrpc_open()` only performs NFSv4 opens for regular files. It computes access and delegation request bits, gets/creates local open state with `nfscl_open()`, optionally tries an open+layout compound for pNFS, installs returned delegations, increments local open counts only after success, and retries on recovery errors. Delegation issue invalidates local attribute cache because pre-delegation attributes may remain cached while a delegation is held.
- `nfsrpc_openrpc()` constructs the NFSv4 `OPEN` compound for claim-fh, claim-null, reclaim, and delegation-claim cases. It parses the returned stateid, result flags, delegation payload, weak attributes, optional `OPEN_CONFIRM`, and optional recursive reopen to obtain a delegation after confirmation. Delegation parsing validates limit modes and ACE XDR before returning a `struct nfscldeleg`.
- `nfsrpc_doclose()` is more than a close RPC. It releases outstanding byte-range locks, sends `LOCKU` and `ReleaseLockOwner`/`FreeStateID`, then serializes close against the open owner rwlock before calling `nfscl_tryclose()`. It relies on being called from inactive paths where no other thread is mutating that open's lock lists.
- `nfsrpc_setclient()` handles both NFSv4.1+ sessions and NFSv4.0 setclientid. For NFSv4.1 it can try `CreateSession` on an existing client ID, otherwise performs `ExchangeID` then `CreateSession`, installs the new session at the mount head, marks old sessions defunct, wakes waiters, configures reconnect backchannel binding when callbacks are enabled, and sends `ReclaimComplete` for non-reclaim setup. For NFSv4.0 it creates a dummy session object for shared fields and sends `SETCLIENTID` plus confirm with callbacks disabled.
- Read/write wrappers split large I/O into negotiated `nm_rsize`/`nm_wsize` chunks. Read rejects offset overflow beyond `nm_maxfilesize`, uses EOF and short-read handling per protocol version, and updates post-op attributes. Write validates one-iovec input, chunks data, optionally implements NFSv4 append by verifying file size first, rolls back `uio` fields on retryable reply errors, tracks the lowest commitment level, updates write verifiers, and deliberately avoids full owner/group attributes in write GETATTR to avoid user/group mapping upcall deadlocks.
- Create and namespace operations translate POSIX operations into version-specific NFS compounds. NFSv4 create is an `OPEN` with create mode plus `GETFH`/`GETATTR` and directory post-op attributes. Remove and rename may prepend delegation returns, retry without them if the delegation return itself fails, and then parse extra `PUTFH`/`GETATTR` operations to classify target vnode status as deleted, link-count zero, or still valid.
- `nfsrpc_lookup()` has special NFSv4 behavior for `"."` and `".."`, plus an optional `LOOKUP+VERIFY+OPEN` fast path. That fast path may create local open state from a successful compound; if a delegation is returned but no vnode is available to invalidate cached attributes, the code returns the delegation immediately.
- `nfsrpc_readdir()` and `nfsrpc_readdirplus()` convert wire entries into 4BSD `struct dirent` records, storing the opaque NFS cookie in hidden space after `d_name`. They only return full `DIRBLKSIZ` chunks or unchanged residual at EOF, synthesize NFSv4 dot/dotdot entries through `LOOKUPP`, validate server-supplied names, zero padding, maintain cookie verifiers, and fill extra empty records to complete directory blocks.
- `nfsrpc_readdirplus()` additionally parses file handles and attributes, acquires or references vnodes via `nfscl_nget()`, avoids dotdot locking to prevent lock-order reversals, checks local modification time against RPC start time before loading attributes, sets directory entry type, and populates the name cache when safe.
- Advisory locking converts `struct flock` into NFS ranges, performs local lock bookkeeping before RPCs, rejects partial-range locks on servers without POSIX locking semantics, and routes operations through `LOCKT`, `LOCK`, `LOCKU`, and lock-owner release. `nfstest_outofseq` can intentionally perturb sequence IDs for testing.
- `statfs`, `pathconf`, and `fsinfo` map protocol differences: NFSv4 obtains filesystem/path configuration through GETATTR attribute bitsets, while NFSv3/v2 use dedicated procedures where available. `statfs` also probes case-insensitivity through `pathconf`.
- pNFS control flow starts with session/device discovery. `nfsrpc_getdeviceinfo()` parses file-layout stripe indices or flex-file address/version lists, chooses TCP endpoints, selects supported NFSv3/NFSv4.1/NFSv4.2 DS protocol versions, returns notification bits, and connects via `nfsrpc_fillsa()`.
- `nfsrpc_fillsa()` builds DS socket requests for IPv4/IPv6, derives Kerberos service principals for pNFS DS connections when needed, reuses sessions by address or server owner where possible, does DS `ExchangeID`/`CreateSession`, handles minor-version fallback, and appends new DS sessions at the mount session tail so later trunked sessions use correct sequence IDs.
- `nfscl_doiods()` is the pNFS data path. It checks pNFS/callback/layout eligibility, pins the client, obtains an I/O stateid, finds or fetches a layout, chooses a file-layout or flex-file path, splits work over layout ranges, reports DS errors through layout error mechanisms for NFSv4.2 where appropriate, updates `lastbyte` and layout-written flags, and rolls back `uio` state for mirrored write retry failures.
- File layout I/O (`nfscl_doflayoutio()`) maps logical offsets to dense or sparse stripe offsets, chooses DS file handles, honors commit-through-MDS, sets `NDSCOMMIT` when DS commits are required, and calls DS read/write/commit RPCs.
- Flex-file I/O (`nfscl_dofflayoutio()`) chooses mirror DS file handles and per-mirror stateids, substitutes loose-coupling user/group credentials, randomly chooses one mirror for reads, writes all mirrors, splits mbuf chains for mirrored writes, and uses async pNFS worker tasks for all but the final mirror write/commit when worker threads are enabled.
- Layout parsing (`nfsrv_parselayoutget()`) validates counts and lengths, constructs `struct nfsclflayout` objects for file and flex-file layout bodies, copies device IDs/stateids/file handles, parses flex-file user/group strings through id-mapping helpers, records layout utility flags, and inserts returned layout segments in increasing offset order only if they match the first returned iomode.

## State And Data Structures

- Global/sysctl state in this chunk includes `vfs.nfs.ignore_eexist`, `vfs.nfs.dssameconn`, `vfs.nfs.maxcopyrange`, `nfs_exchangeboot`, `nfstest_outofseq`, `nfscl_assumeposixlocks`, `nfscl_enablecallb`, `nfsv4_cbport`, and `nfstest_openallsetattr`.
- Core per-mount state used throughout includes `struct nfsmount` fields for protocol version/minor version, mount flags/private flags, max file size, rsize/wsize/readdir size, write verifier, root file handle, mount socket request, session list, client pointer, pNFS/flex-file feature bits, persistent-session bit, case-insensitive bit, and fake-root handling.
- Core per-node state includes `struct nfsnode` file handles, NFSv4 parent/name data, cached attributes, cookie verifier, open state pointer for one-open-owner mounts, named-attribute flags, local modification time, layout disable flag `NNOLAYOUT`, DS commit flag `NDSCOMMIT`, and write-opened state.
- NFSv4 state structures include `struct nfsclclient`, `struct nfsclsession`, `struct nfsclds`, `struct nfsclowner`, `struct nfsclopen`, `struct nfscllockowner`, `struct nfscllock`, `struct nfscldeleg`, and `nfsv4stateid_t`. The code updates open/lock sequence IDs, session IDs/slot tables, delegation stateids, client ID revisions, server-owner strings, and DS write verifiers.
- pNFS layout state includes `struct nfscllayout`, `struct nfsclflayout`, `struct nfscldevinfo`, per-file layout file handles, flex-file mirror descriptors, device IDs, stripe indices, layout offsets/ends, layout stateid, retonclose flag, mirror count, version index, DS address slots, and per-layout written/lastbyte state.
- RPC encoding/decoding state is centralized in `struct nfsrv_descript`, mbuf chains, `NFSM_BUILD`, `NFSM_DISSECT`, `nfsm_strtom`, `nfsm_fhtom`, `nfsm_mbufuio`, `nfsm_uiombuf`, `nfsm_uiombuflist`, `nfsm_stateidtom`, `nfsrv_putattrbit`, `nfsv4_loadattr`, `nfsm_loadattr`, and post-op/WCC helpers.
- `struct nfsclwritedsdorpc` is the shared argument/result record for async mirrored DS writes, commits, and compile-disabled advise calls. It carries task state, vnode, stateid, DS pointer, offset/length, file handle, mbuf, protocol version, credentials, thread pointer, and returned error.

## Dependencies

- Kernel/VFS dependencies include vnodes, mounts, credentials, UIO/iovec, `struct dirent`, `struct flock`, namecache entry helpers, vnode references/locks (`vref`, `vrele`, `vput`, `LK_EXCLUSIVE`), ACL types, POSIX advice constants, socket address structures, taskqueue tasks, sysctls, mbufs, mutexes, sleeps/wakeups, and FreeBSD network/RPC client control paths.
- NFS client infrastructure dependencies include `nfscl_reqstart()`, `NFSCL_REQSTART`, `nfscl_request()`, `newnfs_request()`, `newnfs_connect()`, `newnfs_disconnect()`, `nfs_catnap()`, `nfscl_hasexpired()`, `nfscl_initiate_recovery()`, `nfscl_getstateid()`, `nfscl_open()`, `nfscl_openrelease()`, `nfscl_ownerrelease()`, `nfscl_getcl()`, `nfscl_getref()`, `nfscl_relref()`, `nfscl_getlayout()`, `nfscl_rellayout()`, `nfscl_layoutgetres()` callers, and many NFS XDR conversion helpers.
- NFSv4 id/name mapping and ACL dependencies include `nfsv4_strtouid()`, `nfsv4_strtogid()`, `nfsv4_fillattr()`, `nfsrv_dissectace()`, ACL support flags, and `nfsuserd`-sensitive owner/group attribute mapping noted in write comments.
- pNFS dependencies include layout/device caches, `nfscl_getdevinfo()`, `nfscl_reldevinfo()`, `nfscl_freedevinfo()`, `nfscl_freeflayout()`, `nfscl_dserr()`, `nfsv4_getipaddr()`, `nfs_pnfsio()`, `nfs_pnfsiothreads`, `nfsrpc_bindconnsess`, and optional RPCSEC_GSS service-principal conversion through `rpc_gss_ip_to_srv_principal_call()`.
- Protocol constants and bitsets include many `NFSPROC_*`, `NFSV4OP_*`, `NFSERR_*`, NFSv4 attrbits, file type conversions, write commitment/verifier constants, session/create/exchange flags, pNFS layout types, file-layout utilities, flex-file limits, and NFSv4.1/4.2 minor-version constants.

## Risks And Invariants

- XDR parsing is manually offset-driven. Almost every routine depends on exact compound operation ordering, `ND_NOMOREDATA` propagation, and bounded length/count validation. A missed status word or incorrect skip can desynchronize all subsequent parsing.
- NFSv4 sequence IDs and stateids are fragile invariants. Open owner, lock owner, open stateid, lock stateid, delegation stateid, layout stateid, and session sequencing are updated only after specific request outcomes. Incorrect retry or cleanup can trigger stale/old/bad stateid recovery loops.
- Error handling intentionally distinguishes transport errors from server `nd_repstat`, and many wrappers convert repeated recovery errors to `EIO` after retry limits. Strategy writes are special: recovery-in-progress errors become `EIO` to leave buffers dirty and avoid deadlock with recovery.
- Write paths mutate `uio` while constructing mbufs and must roll it back on server-side failure or mirrored retry. Short writes are accepted in normal write paths with backout of the unwritten tail, but mirrored DS writes treat short writes as I/O errors.
- Directory enumeration relies on private `struct dirent` packing and hidden cookie storage after `d_name`; it assumes system-space, single-iovec, `DIRBLKSIZ`-aligned buffers. Invalid server names are skipped with precise rollback of `uio` and block-size accounting.
- Delegation-return compounds in remove/rename are optimistic. If the embedded `DELEGRETURN` fails, the code frees the reply and retries the namespace operation without it, relying on server recall semantics.
- Fake-root file handle handling modifies mount root file handle state lazily through `nfsrpc_getdirpath()` and may call cross-chunk `nfscl_statfs()` when the root handle is still a sentinel size.
- ACL support is guarded by both global `nfsrv_useacl` and server-supported attribute bits. Setacl is routed through `nfsrpc_setattr()` with a stateid, so it inherits setattr recovery and open-state behavior.
- pNFS DS connection/session reuse depends on matching IP address, server-owner strings, DS/MDS flags, defunct state, and `vfs.nfs.dssameconn`. Bad reuse can direct I/O to the wrong DS session; missed reuse can create redundant sessions.
- Layout and device parsers bound server-supplied counts (`layout count`, `fhcnt`, `stripecnt`, `addrcnt`, flex mirrors, versions) to avoid unbounded allocation. Partial allocation error paths must free layout/device structures without leaking file handles.
- Flex-file loose coupling rewrites credentials from server-provided user/group values. Those values are parsed from strings and id-mapped; failure aborts layout parsing or DS I/O.
- Async mirror helpers share stack-owned/state-owned pointers through `struct nfsclwritedsdorpc`. The waiting loop depends on `done`, `inprog`, task wakeups, held credentials, and fallback-to-inline execution when pNFS worker submission fails.
- Commit verifier handling is split between MDS and DS verifiers. A changed verifier marks `NFSERR_STALEWRITEVERF` or forces `must_commit`, and DS commits set/clear `NDSCOMMIT` on the vnode state.
- Several "ignore retry duplicate" compatibility behaviors are intentionally unsafe-looking but sysctl/protocol scoped: symlink and mkdir may map `EEXIST` to success when `vfs.nfs.ignore_eexist` is set and sessions do not provide exactly-once semantics; rmdir maps `ENOENT` to success as a retry duplicate.

## Cross-Chunk References

- This chunk ends inside `nfsrpc_createlayout()` at line 8651. The remainder of that function in the next chunk emits the name, `SAVEFH`/`GETFH`/`GETATTR`, directory post-op GETATTR, `RESTOREFH`/`LAYOUTGET`, sends the compound, parses state/delegation/layout replies, installs open state, and performs cleanup.
- Prototypes visible in this chunk but definitions after line 8651 include `nfsrpc_getcreatelayout()`, `nfsrpc_layoutgetres()`, `nfsrpc_copyrpc()`, `nfsrpc_clonerpc()`, `nfsrpc_seekrpc()`, `nfsm_split()`, and `nfscl_statfs()`. The current chunk already calls `nfsrpc_getcreatelayout()`, `nfsrpc_layoutgetres()`, `nfsm_split()`, and `nfscl_statfs()`, so the final per-file report should connect those definitions back to the call sites summarized here.
- Later same-file code also covers NFSv4.2 copy/clone/seek and mbuf splitting, which complement the allocate/deallocate/advise operations already covered in this chunk.
- The final per-file merge should preserve that this chunk contains both generic NFS RPC logic and most pNFS DS machinery, while the next chunk completes create+layout handling and newer NFSv4.2 data-management RPCs.

### Chunk 2: lines 8652-9979

# Chunk Research: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_clrpcops.c lines 8652-9979

## Scope

This chunk covers the tail of `nfsrpc_createlayout()` plus pNFS layout-result handling, NFSv4.2 server-side copy/clone/seek RPCs, NFSv4 extended attribute RPCs, an `M_EXTPG`-aware mbuf splitter, NFSv4.1 `BIND_CONN_TO_SESSION`, `OPENATTR`, and a locked-vnode statfs refresh helper. The file is part of `sources/os/bsd/freebsd-src`, which is included by `Docs/research_subset_a.md`.

The range starts inside `nfsrpc_createlayout()`. Lines before this chunk build the beginning of the NFSv4 compound create/open request; this chunk begins at the open claim filename and covers reply parsing and cleanup.

## APIs and Entry Points

- `nfsrpc_createlayout(...)` is a static pNFS create helper. In this visible tail it appends `SAVEFH`, `GETFH`, file `GETATTR`, directory `PUTFH`/`GETATTR`, `RESTOREFH`, and `LAYOUTGET` to an NFSv4 create-as-open compound, then parses open state, delegation state, file/directory attributes, open-owner state, and optional layout data.
- `nfsrpc_getcreatelayout(...)` wraps `nfsrpc_createlayout()` for create paths on pNFS mounts. It chooses flexfile versus file-layout type, sizes the layout reply from the MDS session cache limit, then passes parsed layout segments to `nfsrpc_layoutgetres()`.
- `nfsrpc_layoutgetres(...)` resolves pNFS layoutget results into client layout state. It handles unsupported layout types, fetches missing device info, and calls `nfscl_layout()` to install the layout.
- `nfsrpc_copy_file_range(...)` is the exported NFS client RPC path for `copy_file_range`. It acquires read/write NFSv4 stateids, retries recoverable state/session errors, calls `nfsrpc_copyrpc()`, advances offsets on success, and tells the caller whether a later commit is required.
- `nfsrpc_copyrpc(...)` builds and parses the NFSv4.2 `COPY` compound, including optional atime `SETATTR`, source `GETATTR`, destination `PUTFH`, `COPY`, destination `GETATTR`, write-verifier handling, and synchronous-copy enforcement.
- `nfsrpc_clone(...)` is the exported clone/offload path. It mirrors the copy wrapper retry structure but calls `nfsrpc_clonerpc()` and does not track unstable write commit state.
- `nfsrpc_clonerpc(...)` builds and parses the NFSv4.2 `CLONE` compound with optional atime `SETATTR`, source/destination stateids, optional `toeof` length encoding, and post-clone attributes.
- `nfsrpc_seek(...)` wraps NFSv4.2 `SEEK`, acquiring a read stateid and retrying recoverable NFSv4 state/session errors, including short retry handling for `NFSERR_OPENMODE`.
- `nfsrpc_seekrpc(...)` sends `SEEK` plus `GETATTR`, returning the server-selected offset, EOF indication, and fresh attributes.
- `nfsrpc_getextattr()`, `nfsrpc_setextattr()`, `nfsrpc_rmextattr()`, and `nfsrpc_listextattr()` implement NFSv4 named-attribute get/set/remove/list operations with follow-up `GETATTR` parsing.
- `nfsm_split(struct mbuf *mp, uint64_t xfer)` splits normal mbuf chains through `m_split()` and manually splits `M_EXTPG` external-page mbufs.
- `nfsrpc_bindconnsess(CLIENT *cl, void *arg, struct ucred *cr)` sends NFSv4.1 `BIND_CONN_TO_SESSION` from the RPC reconnect layer and validates the returned session id/direction.
- `nfsrpc_openattr(...)` sends `OPENATTR`, optionally creating the named-attribute directory, then returns its file handle and attributes.
- `nfscl_statfs(...)` is a static helper used when a vnode is already shared-locked. It calls `nfsrpc_statfs()`, refreshes vnode attrs, lease renewal time, mount fsinfo, statfs data, and I/O size.

## Control Flow

`nfsrpc_createlayout()` continues the create/open compound by encoding the target filename, saving the current file handle, requesting the new file handle and attributes, switching back to the parent directory to fetch post-op directory attributes, restoring the new file handle, and issuing `LAYOUTGET`. After `nfscl_request()`, it records any compound status as `laystat`, increments the open-owner sequence id, and parses the open result if reply data remains.

Open reply parsing extracts the returned stateid, accepted attribute bits, and delegation discriminant. Read/write delegations allocate `struct nfscldeleg`, copy credentials, initialize owner/lock lists and a delegation rwlock, parse delegation stateid, recall flag, write-size limit, and ACE. `DELEGATENONEEXT` is accepted only for NFSv4.1+ and optionally skips contention/resource detail. Any unknown delegation encoding is treated as bad XDR. The function then checks `SAVEFH`, calls `nfscl_mtofh()` for the created file handle/attributes, parses parent directory postop attributes, creates/updates client open state with `nfscl_open()`, stores the returned open stateid, releases that open state, marks `unlockedp`, and finally parses `RESTOREFH`/`LAYOUTGET`. A failed layoutget after a successful open is preserved as `laystat` rather than failing the create itself.

`nfsrpc_getcreatelayout()` initializes a temporary layout segment list, calls `nfsrpc_createlayout()`, and always routes the layout status through `nfsrpc_layoutgetres()`. If layoutget succeeded it passes the new file handle; otherwise it passes no file handle so layout-result handling can still process layout-type fallback state. Installed layouts are immediately released with `nfscl_rellayout(lyp, 0)` because `nfscl_layout()` returns a referenced/shared-locked layout.

`nfsrpc_layoutgetres()` first reacts to `NFSERR_UNKNLAYOUTTYPE`: flexfile mounts fall back to file layout by clearing `NFSSTA_FLEXFILE`; file-layout failure disables pNFS by clearing `NFSSTA_PNFS | NFSSTA_FLEXFILE`. For successful layout replies, it walks every parsed file-layout segment and every flexfile mirror where applicable. It first tries to bind existing device information with `nfscl_adddevinfo(nmp, NULL, ...)`; on a miss it fetches device info with `nfsrpc_getdeviceinfo()` and retries the add. Only after device resolution does it call `nfscl_layout()` to install the layout and optionally report that the returned layout is locked.

`nfsrpc_copy_file_range()` and `nfsrpc_clone()` share the same high-level loop. Each iteration gets source read and destination write stateids, calls the RPC worker, dereferences any state locks returned by `nfscl_getstateid()`, sleeps on grace/delay/stale/bad-session/old-stateid conditions, initiates client recovery for stale stateids, checks client expiration on expired/bad-stateid errors, and converts persistent failures to `EIO`. On success they advance input and output offsets by the length actually completed.

`nfsrpc_copyrpc()` caps requested length to `nfs_maxcopyrange`, zeroes `*lenp` before the RPC, and optionally prepends source atime `SETATTR` unless the mount is `MNT_NOATIME`. The `COPY` operation requests synchronous server-side copy and no callback IDs. Reply parsing validates that no callback IDs are returned, extracts copied length, commit mode, and write verifier, updates the mount write verifier under `NFSLOCKMNT()`, rejects verifier changes with `NFSERR_STALEWRITEVERF`, requires the server's synchronous flag to be true, loads destination attributes with `NFS_LATTR_NOSHRINK`, and stores the copied length only if the compound remained successful. `NFSERR_OFFLOADNOREQS` is translated to `NFSERR_NOTSUPP` when synchronous or consecutive-copy requirements cannot be met.

`nfsrpc_clonerpc()` is structurally similar to `nfsrpc_copyrpc()` but sends `CLONE`, treats `len == 0` as a no-op, encodes `toeof` as a zero clone length, and has no commit/verifier handling. On clone failure it sets `*lenp = 0`; on success the wrapper advances by the caller's length.

`nfsrpc_seek()` obtains a read stateid and calls `nfsrpc_seekrpc()` until the state/session error policy says to stop. `nfsrpc_seekrpc()` sends `SEEK` at the caller's offset for the requested content class, then a `GETATTR`. Successful replies overwrite `*eofp` and `*offp`, then load attributes.

The extended attribute functions all append a `GETATTR` so VFS callers can refresh attribute cache state. `getextattr` copies or skips the returned value depending on whether `uiop` is present and large enough. `setextattr` validates the outgoing value fits `nd_maxreq`, encodes `NFSV4SXATTR_EITHER`, and writes the uio into the request. `rmextattr` encodes only the name. `listextattr` sends a cookie and max length, then converts each server string into FreeBSD extattr list format by prefixing a one-byte name length, tracking truncation by setting `*eofp = false`.

`nfsm_split()` delegates ordinary mbufs to `m_split()`. For `M_EXTPG`, it locates the split mbuf and page, splits at mbuf boundaries when possible, otherwise allocates a new external-page mbuf and, when splitting inside a page, allocates a fresh wired page and copies the trailing bytes into it. Physical page references after the split page are moved into the new mbuf; lengths, first/last page offsets, and `m_next` links are adjusted in place.

`nfsrpc_bindconnsess()` manually sends a compound over a reconnecting RPC client with 30 second timeout and temporary UNIX auth. It realigns the reply, reads the compound status, skips the tag, checks the returned session id matches `nfscl_reconarg.sessionid`, and expects `NFSCDFS4_BOTH`. It prints diagnostics rather than returning errors because it is a reconnect callback.

`nfsrpc_openattr()` uses `newnfs_request()` directly against `nm_sockreq` instead of the usual vnode macro, then parses `GETFH` and postop attributes. `nfscl_statfs()` updates lease renewal under `NFSLOCKCLSTATE()` and mount cached filesystem/statfs data under `nm_mtx`.

## State and Synchronization

- `nfsrpc_createlayout()` mutates open-owner sequence state through `NFSCL_INCRSEQID()`, client delegation flags `NFSCLFLAGS_FIRSTDELEG | NFSCLFLAGS_GOTDELEG`, returned delegation/open structures, `attrflagp`, `dattrflagp`, `unlockedp`, and `laystatp`.
- Delegation allocation in `nfsrpc_createlayout()` owns `dp` until success assigns `*dpp = dp`; errors free it with `M_NFSCLDELEG`.
- Layout-result handling mutates mount pNFS capability flags under `NFSLOCKMNT()` and installs device/layout cache entries through `nfscl_adddevinfo()` and `nfscl_layout()`.
- Copy/clone/seek wrappers hold temporary state locks returned by `nfscl_getstateid()` and always drop them with `nfscl_lockderef()` after each RPC attempt.
- Copy reply parsing protects `nmp->nm_verf` and `NFSSTA_WRITEVERF` updates with `NFSLOCKMNT()`.
- `nfscl_statfs()` updates client lease renewal under the global client-state lock and mount stat/fsinfo under `nm_mtx`.
- `nfsm_split()` mutates mbuf page arrays and chain links directly; callers must already own the mbuf chain.

## Dependencies

This chunk depends heavily on FreeBSD NFS client XDR helpers and compound RPC machinery: `NFSCL_REQSTART`, `nfscl_reqstart`, `NFSM_BUILD`, `NFSM_DISSECT`, `nfsm_strtom`, `nfsm_fhtom`, `nfsm_stateidtom`, `nfsm_uiombuf`, `nfsm_mbufuio`, `nfsm_advance`, `nfsm_loadattr`, `nfsm_getfh`, `nfscl_postop_attr`, `nfsrv_putattrbit`, `nfsrv_getattrbits`, `nfsrv_setuplayoutget`, `nfsrv_parselayoutget`, `nfsrv_dissectace`, `nfscl_request`, and `newnfs_request`.

NFS client state dependencies include `nfsmount`, `nfsnode`, `nfsfh`, `nfsclowner`, `nfsclopen`, `nfscldeleg`, `nfsclsession`, `nfscllayout`, `nfsclflayout`, `nfscldevinfo`, `nfscl_getstateid()`, `nfscl_open()`, `nfscl_openrelease()`, `nfscl_rellayout()`, `nfscl_initiate_recovery()`, `nfscl_hasexpired()`, `nfs_catnap()`, `nfscl_loadattrcache()`, `nfscl_loadfsinfo()`, `nfscl_loadsbinfo()`, and `newnfs_iosize()`.

Protocol dependencies include NFSv4.1 sessions/pNFS operations (`SAVEFH`, `RESTOREFH`, `LAYOUTGET`, `GETDEVICEINFO`, `BIND_CONN_TO_SESSION`, file and flexfile layouts), NFSv4.2 operations (`COPY`, `CLONE`, `SEEK`), NFSv4 named attributes (`OPENATTR`, get/set/list/remove extattr procedures), stateid semantics, delegation encodings, write verifiers, commit modes, and NFS error classes.

Kernel infrastructure dependencies include vnodes/mounts/credentials/uio, mbufs including `M_EXTPG`, physical direct-map access, VM page allocation, RPC `CLIENT` calls, temporary auth creation/destruction, mutexes, and mount flags such as `MNT_NOATIME`.

## Risks and Edge Cases

- The chunk starts after `nfsrpc_createlayout()` request initialization, so correct operation depends on the previous chunk's open-owner, create-mode, and compound op count setup matching the reply parsing performed here.
- `nfsrpc_createlayout()` returns immediately on transport-level `nfscl_request()` error without freeing `nd->nd_mrep`; this follows local convention only if no reply mbuf is owned on that path.
- Layoutget failure after successful create/open is intentionally non-fatal. Callers must inspect `laystat`/layout cache behavior rather than assuming a successful create implies pNFS availability.
- `nfsrpc_getcreatelayout()` passes `laystat` through layout handling but returns only the create/open `error`; pNFS fallback/disable decisions can occur without changing the create return value.
- `nfsrpc_layoutgetres()` prints but otherwise continues after a second `nfscl_adddevinfo()` failure, leaving the final `laystat` nonzero only if that function set it. Device-cache insertion failures can degrade layout installation.
- Copy and clone wrappers pass `NULL` credentials to `nfscl_getstateid()` for both source and destination, whereas seek passes `cred`. Correct state selection depends on `nfscl_getstateid()` fallback rules.
- `nfsrpc_copyrpc()` requires synchronous copy support and rejects asynchronous copy behavior with `NFSERR_NOTSUPP`; it also treats write-verifier changes as stale verifier errors, forcing conservative fallback/retry behavior.
- `nfsrpc_clonerpc()` sets local `len = 0` for `toeof` but does not update `*lenp` on success. The wrapper advances offsets by the caller-provided length, so callers must pass a meaningful length even when requesting clone-to-EOF.
- In `nfsrpc_seekrpc()`, any local XDR/loadattr error can be overwritten by `error = nd->nd_repstat` after the success block. If `nfsm_loadattr()` fails while `nd_repstat` is zero, the local error appears lost.
- `getextattr` returns `ENOATTR` if the server returns data but the uio path is absent or length checks fail outside the explicit length-query path. It also reports the full server length even when the caller's uio was shorter and the data was truncated/skipped successfully.
- `listextattr` stores each name length in a single `u_char`; the preceding `EXTATTR_MAXNAMELEN` check must remain within 255 for this format to be safe.
- `nfsm_split()` can panic on inconsistent `M_EXTPG` accounting, uses blocking allocation, wires a new page for intra-page splits, and transfers page physical addresses without clearing moved slots in the original mbuf.
- `nfsrpc_bindconnsess()` leaks the request mbuf on early RPC failure or null reply unless `CLNT_CALL_MBUF()` consumes it by contract. The visible code only frees `nd_mrep`.

## Cross-Chunk References

- Earlier lines in this file define prototypes for the static helpers in this chunk and call `nfscl_statfs()` from several RPC paths when lease/fsinfo refresh is needed.
- The previous chunk contains the beginning of `nfsrpc_createlayout()` and the related `nfsrpc_getopenlayout()` path. It establishes the open/create compound setup consumed by the reply parser here.
- Earlier layout paths call `nfsrpc_layoutgetres()` for normal layoutget/open layout results; this chunk supplies the shared device-info resolution and layout installation routine.
- Earlier write paths call `nfsm_split()` when a transfer must split an mbuf chain, including external-page mbuf support.
- Earlier session/reconnect setup stores `nfsrpc_bindconnsess` in the reconnect argument callback used by `sys/rpc/clnt_rc.c`.
- `sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_clvnops.c` calls the exported RPCs here from VOP implementations: `nfs_copy_file_range()` selects `nfsrpc_clone()` or `nfsrpc_copy_file_range()`, seek/data-hole operations call `nfsrpc_seek()`, extended-attribute VOPs call the extattr RPCs, and named-attribute paths call `nfsrpc_openattr()`.
- `sources/os/bsd/freebsd-src/sys/fs/nfs/nfs_var.h` declares the exported functions visible outside this file, including copy, clone, seek, extattr, and openattr RPC entry points.
- The final per-file report should merge this chunk with adjacent chunk research rather than being generated from this chunk alone.
