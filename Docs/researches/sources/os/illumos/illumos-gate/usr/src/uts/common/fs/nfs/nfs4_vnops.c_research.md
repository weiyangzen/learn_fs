# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_vnops.c

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-9830, source bytes 262136, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_nfs_nfs4_vnops_c_1_473a3c3ffae8_research.md`
- chunk 2: lines 9831-16006, source bytes 167484, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_nfs_nfs4_vnops_c_2_a52383817e0a_research.md`

## Chunk Research

### Chunk 1: lines 1-9830

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_vnops.c lines 1-9830

## Scope

This chunk covers the first 9,830 lines of illumos' NFSv4 vnode operations implementation. It is in subset A via `sources/os/illumos/illumos-gate`, and it is the main bridge between illumos VFS/vnode/page-cache entry points and NFSv4 COMPOUND operations for open, close, reads, writes, metadata, directory namespace operations, readdir, and the start of VM paging.

The chunk ends inside `nfs4_getapage()` at its local variable declarations. The rest of `nfs4_getapage()` plus later putpage, commit, mmap, lock, ACL, and pathconf code are cross-chunk responsibilities.

## APIs And Entry Points

- Vnode op table: `nfs4_vnodeops_template` registers NFSv4 implementations for open, close, read, write, ioctl, getattr/setattr/access, lookup/create/remove/link/rename/mkdir/rmdir/symlink/readdir/readlink, fsync, inactive, fid, rwlock/rwunlock, seek, page/mmap/pageio/dispose, security attributes, share locks, and vnode events.
- Exported or externally referenced vnode helpers in this chunk include `nfs4_getvnodeops()`, `nfs4_getattr()`, `nfs4_inactive()`, `nfs4_lookup()`, `nfs4_fid()`, `nfs4_rwlock()`, and `nfs4_rwunlock()`.
- NFSv4 compound argument helpers include `nfs4args_lookup_free()`, `nfs4args_lock_free()`, `nfs4args_lockt_free()`, `nfs4args_setattr()`, `nfs4args_setattr_free()`, `nfs4args_verify()`, `nfs4args_verify_free()`, `nfs4args_write()`, and `nfs4args_copen_free()`.
- Main protocol operations implemented here: `nfs4open_otw()`, `nfs4_reopen()`, `nfs4close_otw()`, `nfs4read()`, `nfs4write()`, `nfs4setattr()`, `nfs4openattr()`, `nfs4lookupvalidate_otw()`, `nfs4lookupnew_otw()`, `call_nfs4_create_req()`, `nfs4_remove()`, `nfs4_link()`, `nfs4rename_persistent_fh()`, `nfs4rename_volatile_fh()`, and `nfs4readdir()`.
- VM/page-cache entry points covered to the boundary: `nfs4_getpage()` is complete, and `nfs4_getapage()` begins at line 9823 but continues in the next chunk.

## Control Flow

### Initialization And Vnode Dispatch

The file starts with kernel, RPC, NFS, VM, and autofs dependencies, then declares many local helpers shared by later sections. `nfs4_vnodeops_template` maps illumos VOP names to NFSv4 functions. Several functions are intentionally non-static because ephemeral mount stub vnode ops call them from outside this source file.

### Open, Reopen, Close

`nfs4_open()` rejects wrong-zone access, bypasses OTW open for non-regular files via `nfs4_open_non_reg_file()`, obtains the parent vnode and file name, handles just-created vnodes and DNLC insertion, forces `FWRITE` for truncating opens, and delegates real NFSv4 open work to `nfs4open_otw()`. Shadow vnodes may be exchanged for master vnodes after success.

`nfs4open_otw()` builds several OPEN compounds:

- normal open: `PUTFH(dir), OPEN, GETFH, GETATTR(file)`;
- create without setgid repair: `PUTFH(dir), SAVEFH, OPEN(create), GETFH, GETATTR(file), RESTOREFH, GETATTR(dir)`;
- create with setgid repair: `PUTFH(dir), OPEN(create), GETFH, GETATTR(file), SAVEFH, PUTFH(dir), GETATTR(dir), RESTOREFH, NVERIFY(owner_group), SETATTR(owner_group)`.

It synchronizes open-owner sequence IDs, decides whether an OTW open is necessary for delegations and cached state, handles exclusive create verifiers, converts `vattr_t` to NFSv4 attributes against server-supported attribute masks, sends `rfs4call()`, starts recovery on recoverable errors, handles `OPEN_CONFIRM`, compares returned filehandles with cached vnodes, creates or updates rnodes via `makenfs4node()`, updates open streams and stateids, accepts delegations, updates directory caches, and handles exclusive-create follow-up `SETATTR`. Lost requests are captured by `nfs4open_save_lost_rqst()` for timeout/interruption/forced-unmount recovery.

`nfs4_reopen()` reopens an existing `nfs4_open_stream_t` during recovery or delegation transitions. It chooses `CLAIM_NULL`, `CLAIM_PREVIOUS`, or `CLAIM_DELEGATE_CUR`, can reuse recovered delegation state without OTW open, handles `NO_GRACE`, `GRACE`, `DELAY`, `FHEXPIRED`, `BAD_SEQID`, `WRONGSEC`, `EXPIRED`, and access fallback credentials, verifies that volatile/persistent filehandles still identify the same object, updates open stream stateids and delegation fields, or marks the rnode/open stream failed via `nfs4_fail_recov()`.

`nfs4_close()` releases local or network locks, flushes dirty pages with `nfs4_putpage_commit()` on final writer close, gathers delayed rnode errors, skips OTW close for non-regular files, and then calls `nfs4close_one()` for regular files. `nfs4close_otw()` sends `PUTFH, GETATTR, CLOSE`, updates open-owner seqids, saves lost close requests, starts recovery, invalidates cache on non-recoverable RPC errors, updates close stateid, invalidates the open stream, decrements the open-stream reference obtained at OPEN, and caches post-close attributes.

### Read And Write

`nfs4_read()` validates type, zone, offsets, recovery-error state, and then either bypasses VM caching for `VNOCACHE`/direct I/O or copies through segmap/VPM after `nfs4_validate_caches()`. It waits for cache purges and respects current `r_size`.

`nfs4_write()` validates type/zone/limits, serializes append writes by upgrading to writer lock, checks `RLIMIT_FSIZE`, increments delegation change for write delegations, and enters `r_lkserlock`. It writes either through direct `nfs4write()` with a temporary kernel buffer or through segmap/VPM and `writerp4()`. It throttles dirty-page creation using `r_awcount`, `r_gcount`, and `mi_max_threads`; forces synchronous release for `FSYNC`, `FDSYNC`, noac, swap, or out-of-space state; restores `uio` state on error; and updates local delegated mtime/ctime on success.

`nfs4write()` sends repeated `PUTFH, WRITE` compounds using the current write stateid from `nfs4_get_w_stateid()`. It handles stateid fallback (`OLD_STATEID`, `BAD_STATEID` on delegation), delegation return/reopen, recovery, server short/oversized writes, unstable write verifiers, kstats, attr-cache purge, `R4WRITEMODIFIED`, and local mtime/ctime updates.

`nfs4read()` sends repeated `PUTFH, READ` compounds using `nfs4_get_stateid()`. It supports direct copy into a caller `uio` or a mapped buffer, handles sync versus async stateid retry rules, delegation return on bad delegation stateid, recovery, EOF, kstats, and residual reporting.

`nfs4_rdwrlbn()` wraps a page list in a `buf`, maps it, selects `UNSTABLE4` for async writes when memory pressure allows, calls `nfs4_bio()`, and marks pages with commit state (`C_DELAYCOMMIT` or `C_NOCOMMIT`). `nfs4_bio()` dispatches page I/O reads to `nfs4read()` and writes to `nfs4write()`, rotating through OTW credentials/open streams on `EACCES`, zero-filling EOF tails, translating beyond-EOF full misses to `NFS_EOF`, recording write errors and stale state, and releasing any open stream obtained for credential selection.

### Attributes, Access, Symlinks, Inactive

`nfs4_getattr()` provides fast `ATTR_HINT` answers for size/fsid/rdev from cached rnode fields, flushes dirty pages before mtime queries unless a write delegation makes local mtime authoritative, and then delegates to `nfs4getattr()`.

`nfs4setattr()` flushes dirty data first, optionally builds guarded size-changing compounds using `GETATTR, VERIFY(ctime), SETATTR, GETATTR`, converts vnode and ACL attributes to NFSv4 fattrs, chooses stateid for size changes, retries when ctime verification fails, handles stateid fallback and recovery, purges access and ACL caches on uid/gid/mode changes, invalidates pages after truncation, updates attr/ACL caches from final GETATTR, sets `r_size` on successful size change, and may issue a mode-repair SETATTR after uid/gid changes if the server clears setuid/setgid unexpectedly. `nfs4_compare_modes()` supports that repair decision.

`nfs4_access()` maps VFS read/write/exec requests to NFSv4 `ACCESS4_*`, checks read-only mounts, validates caches when an access cache exists, tries cached access results including `crnetadjust()` credentials, sends `PUTFH, ACCESS[, GETATTR]`, handles recovery and stale filehandles, caches access results, and retries adjusted credentials for setuid-root semantics.

`nfs4_readlink()` serves cached symlink contents when valid, otherwise sends `PUTFH, READLINK, GETATTR`, converts UTF-8 link data to a local string, optionally caches it, updates attributes, and maps NFSv4's non-symlink `ENXIO` behavior to VFS `EINVAL`.

`nfs4_fsync()` flushes and commits dirty pages unless `FNODSYNC` or swap vnode applies. `nfs4_inactive()` avoids doing OTW cleanup inline when open streams, delegations, or unlinked-open rename state exist; it schedules `nfs4_async_inactive()` in those cases or frees the rnode directly. `nfs4_inactive_otw()` closes all regular-file open streams, flushes dirty data for unlinked-open files, removes `.nfs*` temporary names with recovery retry, and finally adds the rnode to the free list.

### Lookup And Extended Attributes

`nfs4_lookup()` handles xattr lookup redirection, takes the directory reader lock, calls internal `nfs4lookup()`, and wraps device vnodes with `specvp()`.

`nfs4lookup()` handles empty name, non-directory checks, `"."` access checks, DNLC lookup, negative entries, attribute validity, cache purge completion, and chooses either `nfs4lookupnew_otw()` or `nfs4lookupvalidate_otw()`.

`nfs4lookupvalidate_otw()` validates an existing DNLC entry by sending `PUTFH(dir), NVERIFY(change), GETATTR(dir), ACCESS(dir), LOOKUP/LOOKUPP, GETFH, GETATTR(child)`. If the directory change value differs, it purges caches, installs new dir attrs and access, rechecks lookup permission, refreshes or replaces the DNLC entry, handles negative caching, creates child vnodes with `makenfs4node()` or `nfs4_make_dotdot()`, and handles referrals and `WRONGSEC` by direct `SECINFO`.

`nfs4lookupnew_otw()` handles a fresh miss with `PUTFH, SAVEFH, LOOKUP/LOOKUPP, GETFH, GETATTR(child), RESTOREFH, NVERIFY(change), GETATTR(dir), ACCESS(dir)`. It has similar referral, `WRONGSEC`, directory cache, access cache, node creation, and negative DNLC behavior.

`nfs4lookup_setup()` constructs multi-component lookup compounds for secinfo and path traversal, including modes that request no attributes, all intermediate attributes, final named-attribute object attributes, or hidden xattr directory attributes. It allocates the arg array, splits path components in-place, skips `"."`, maps `".."` to `LOOKUPP`, maps `XATTR_RPATH` to `OPENATTR` in xattr modes, inserts `GETFH/GETATTR` as requested, and returns the final lookup op index.

`nfs4openattr()` sends `PUTFH, OPENATTR, GETFH, GETATTR`, caches unsupported xattrs as `NFS4_XATTR_DIR_NOTSUPP`, creates an xattr directory vnode marked `V_XATTRDIR`, stores it in `r_xattr_dir`, and invalidates xattr pathconf cache.

### Namespace Mutation

`nfs4_create()` handles empty-name remote file mount truncation, forced OTW lookup to avoid unsafe create decisions from DNLC, exclusive versus guarded create mode, existing-file access and truncation, special vnode wrapping, regular file create/open via `nfs4open_otw()`, non-regular create via `nfs4mknod()`, mandatory-lock rejection, `EEXIST` retry for retransmitted guarded create, and create/truncate vnode events.

`call_nfs4_create_req()` implements mkdir, symlink, and mknod-style create compounds. It handles setgid inheritance for directories, constructs either `PUTFH,SAVEFH,CREATE,GETFH,GETATTR,RESTOREFH,GETATTR(dir)` or the setgid repair variant with `NVERIFY/SETATTR`, converts attributes using server-supported masks, removes DNLC entries before the call, performs recovery retry, creates the result vnode, updates directory caches from change info and post-op dir attrs, and tolerates some post-create setattr/getattr failures by purging attrs.

`nfs4mknod()` maps VCHR/VBLK/VFIFO/VSOCK to NFSv4 object types, calls `call_nfs4_create_req()`, tries a fallback gid setattr if needed, and wraps device vnodes with `specvp()`.

`nfs4_remove()` looks up the target, rejects directories, removes DNLC entries, detects open files via open streams or vnode references, renames open targets to `.nfs*` names for unlink-open semantics, otherwise flushes dirty pages, returns delegations, sends `PUTFH(dir), REMOVE, GETATTR(dir)`, handles recovery and stale purging, updates directory caches, and emits remove events.

`nfs4_link()` requires server link support, resolves real source vnode, sends `PUTFH(source), SAVEFH, PUTFH(targetdir), LINK, GETATTR(dir), RESTOREFH, GETATTR(source)`, updates source attrs, creates a shadow vnode for the new link name, updates target directory caches, disables `MI4_LINK` on `EOPNOTSUPP`, and emits link events.

`nfs4rename()` orchestrates high-level rename semantics. It locks source and target directories in address order, rejects `"."` and `".."`, handles active existing targets by link-or-rename to a temporary `.nfs*` name, prevents renaming a directory into itself, returns delegations on source and target, chooses persistent or volatile filehandle rename based on mount filehandle-expiry flags, handles servers that return `NFS4ERR_FILE_OPEN` after a link workaround, updates unlinked-open state, removes stale `".."` and readdir caches for moved directories, updates vnevents, and releases held vnodes.

`nfs4rename_persistent_fh()` sends `PUTFH(srcdir), SAVEFH, PUTFH(tgtdir), RENAME, GETATTR(tgtdir)[, PUTFH(srcdir), GETATTR(srcdir)]`, updates directory caches, moves the stored filename with `fn_move()`, updates parent directory filehandle state when moving across directories, maps `ENOTEMPTY` to `EEXIST`, and stores the NFS status for caller special handling.

`nfs4rename_volatile_fh()` protects against concurrent expired-filehandle recovery with `R4RECEXPFH`, sends a larger compound that looks up old and new filehandles around the rename, updates target/source directory caches, updates the renamed object's path and filehandle via `nfs4rename_update()`, updates attributes from post-rename GETATTR, and releases the recovery exclusion flag.

`nfs4_mkdir()`, `nfs4_rmdir()`, and `nfs4_symlink()` are thin wrappers around create/remove helpers with VFS-specific validation. `nfs4_rmdir()` rejects removing current directory, verifies the target is a directory, purges DNLC and readdir caches, maps `ENOTEMPTY` to `EEXIST`, updates directory caches, and emits rmdir events. `nfs4_symlink()` honors `MI4_SYMLINK`, creates an NF4LNK object, and seeds the symlink cache.

### Readdir And VM Boundary

`nfs4_readdir()` validates and possibly purges the readdir cache, short-circuits known EOF cookies, uses `rddir4_cache_lookup()`, fills cache entries synchronously with `nfs4readdir()` or asynchronously with `nfs4_async_readdir()`, copies cached dirents to the caller, updates `uio_loffset` to the next NFSv4 cookie, marks EOF cache entries, and triggers readahead only after lookup activity (`R4LOOKUP`).

`nfs4readdir()` sends `PUTFH, READDIR` or `PUTFH, READDIR, LOOKUPP, GETFH, GETATTR(parent)` when it must synthesize correct `".."` inode information. It requests full vnode attrs plus filehandle when lookup-heavy or first-read flags require it, otherwise requests only rdattr error and possibly mounted-on-fileid. It handles recovery, cookie verifiers, dot/dotdot synthesis, parent DNLC creation, kstats, and preserves mount security flavor if a stub/crossed mount is encountered.

`nfs4_fid()` returns `EREMOTE`. `nfs4_rwlock()` chooses reader lock for reads and for direct I/O with no maps/pages, otherwise writer lock; `nfs4_rwunlock()` releases it. `nfs4_seek()` accepts directory cookies as seek offsets and rejects negative non-directory seeks.

`nfs4_getpage()` validates zone, maps shadow to real vnode, rejects `VNOMAP`, returns `PROT_ALL`, validates caches, throttles page creation behind async writes and getattr pagewalks, rejects non-kernel accesses beyond EOF, calls `pvn_getpages(nfs4_getapage, ...)`, retries after `NFS_EOF` by purging caches, and purges stale filehandles on `ESTALE`.

## State And Data Structures

- `rnode4_t` fields heavily manipulated: `r_flags`, `r_attr`, `r_size`, `r_change`, `r_fh`, `r_server`, `r_dir`, `r_direof`, `r_cookieverf4`, `r_symlink`, `r_xattr_dir`, `r_unldvp/r_unlname/r_unlcred`, `r_open_streams`, `r_deleg_type`, `r_deleg_stateid`, delegation recovery/recall flags, `created_v4`, `r_error`, `r_awcount`, `r_gcount`, `r_count`, `r_mapcnt`, `r_inmap`, `r_nextr`, and write verifier fields.
- `mntinfo4_t` supplies zone, mount flags (`MI4_NOCTO`, `MI4_GRPID`, `MI4_DIRECTIO`, `MI4_NOAC`, `MI4_LINK`, `MI4_SYMLINK`, recovery failure), current server, transfer sizes, async thread limits, attr-cache timing bounds, filehandle expiry policy, recovery thread identity, kstats, and mount security information.
- NFSv4 client state objects include open owners (`nfs4_open_owner_t`), open streams (`nfs4_open_stream_t`), stateids (`stateid4`, `nfs4_stateid_types_t`), lost request records (`nfs4_lost_rqst_t`), recovery state (`nfs4_recov_state_t`), delegations, and bad-seqid recovery entries.
- Local caches include DNLC entries, negative DNLC entries via `DNLC_NO_VNODE`, readdir cache entries (`rddir4_cache` flags `RDDIRREQ/RDDIR/RDDIRCACHED`), attr cache, access cache, ACL cache, symlink contents cache, xattr directory cache, pathconf xattr validity, VM pages, and page commit state in `p_fsdata`.
- Synchronization uses rnode locks (`r_rwlock`, `r_statelock`, `r_statev4_lock`, `r_os_lock`, `r_lkserlock`), mount/server locks, open stream sync locks, open-owner sequence-id synchronization, CVs on `r_cv`, and address-space range locks for later mmap setup. Directory mutations take writer locks; lookups/readdir use reader locks.

## Dependencies

- illumos VFS/vnode interfaces: `VOP_*`, vnode refs, `specvp()`, `vn_ismntpt()`, `vnevent_*`, `fs_vnevent_support`, pathconf/security attrs, share locks.
- VM/page cache: segmap/VPM, `pvn_getpages`, `pageio_setup`, `page_create_va`, `page_lookup`, page locks, `hat_setmod`, `bp_mapin/out`, `pvn_read_kluster`, readahead/async putpage queues.
- NFSv4 RPC/XDR/protocol: `COMPOUND4args_clnt`, `nfs_argop4`, `nfs_resop4`, `rfs4call()`, `xdr_free()`, NFSv4 ops and statuses, stateid helpers, `geterrno4()`, `nfs4_needs_recovery()`, `nfs4_start_recovery()`, `nfs4_start_op/fop()`, `nfs4_end_op/fop()`, open confirm, delegation return/accept, SECINFO/referral handling.
- Name and filehandle helpers: `makenfs4node()`, shared filehandles (`sfh4_get/rele/update`), shadow vnode helpers, `fn_get/fn_move`, `vtoname()`, `vtodv()`, `nfs4_make_dotdot()`, `nfs4rename_update()`.
- Credentials/security: `cred_t`, `crhold/crfree`, `crnetadjust()`, `nfs4_get_otw_cred*()`, access cache, ACL conversion/cache helpers, owner mapping/bad owner logging.
- Kernel diagnostics and accounting: DTrace probes, kstats, LWP I/O stats, debug globals, `cmn_err/zcmn_err`, zone checks.

## Risks And Edge Cases

- Recovery correctness is central. Almost every OTW path must pair `nfs4_start_op/fop()` with `nfs4_end_op/fop()`, free XDR results on all non-RPC-error paths, and reset allocated argument fattrs. Several comments call out deadlock risks if cache purge or getattr is called before ending an operation.
- Open-owner sequence IDs are fragile. `OPEN`, `OPEN_CONFIRM`, and `CLOSE` update seqids only when server replies require it, and lost request handling preserves enough information for recovery. `BAD_SEQID` has retry limits in open paths.
- Delegation stateid fallback is subtle. Reads/writes/setattr handle `OLD_STATEID` and `BAD_STATEID` outside generic recovery to rotate from delegation stateids to open/special stateids or force delegation return and reopen.
- Create and rename preserve POSIX semantics over NFSv4. Guarded creates avoid retransmit truncation; exclusive creates require a post-create SETATTR and cleanup on failure; unlink-open and rename-over-open use temporary `.nfs*` names; active rename targets may need link fallback or double rename depending on server behavior.
- Directory cache coherency relies on change attributes, DNLC purge/update, readdir-cache purge, access-cache refresh, and post-op dir GETATTR. Misbehaving servers that fail to update directory attrs can require `nfs_disable_rddir_cache`.
- Filehandle volatility affects rename and reopen. Persistent handles allow simpler cache/path updates; volatile handles require post-rename lookup/getfh and careful exclusion from expired-FH recovery.
- Zone mismatches generally return `EIO`/`EPERM`, and inactive cleanup may be punted asynchronously to the correct zone.
- Direct I/O, `VNOCACHE`, mmap, mandatory locks, and lost lock recovery interact. This chunk rejects or bypasses caching in several cases; later chunk code continues mmap/lock handling.
- Page I/O has data-loss guardrails around `R4MODINPROGRESS`, async write throttling, unstable writes/commit verifiers, EOF zero-fill, stale flags, and delayed write errors.
- Some code paths intentionally tolerate post-op GETATTR failures after a mutating op while purging caches instead of reporting failure, preserving operation success semantics but relying on later validation.

## Cross-Chunk References

- `nfs4_getapage()` starts at line 9823 and continues after this chunk. The next chunk must cover its actual page fault/read clustering and readahead behavior beyond the declarations visible here.
- Prototypes in this chunk for `nfs4_sync_pageio()`, commit helpers, mmap/addmap/delmap, locking, share locking, ACL/security attr, pathconf, update-dircache, attr-cache update, and local lock recovery are implemented later in the file.
- Functions used here but defined elsewhere in the NFSv4 client include recovery framework helpers, state/open-owner helpers, delegation helpers, rnode creation/cache helpers, readdir cache helpers, page async helpers, SECINFO/referral handling, and NFSv4 attribute conversion.

### Chunk 2: lines 9831-16006

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_vnops.c lines 9831-16006

## Scope

This chunk covers the tail of NFSv4 vnode VM/page-cache handling, page writeback and COMMIT logic, mmap add/delete bookkeeping, pathconf/ACL/share-lock helpers, directory cache update helpers, OPEN_CONFIRM, the main NFSv4 byte-range lock implementation, close-state cleanup, and lock-state reinstitution after lost requests. The source tree `sources/os/illumos/illumos-gate` is included by `Docs/research_subset_a.md`.

The requested range starts inside `nfs4_getapage()`; its function header and initial cache-validation call are just above the chunk boundary.

## APIs and Entry Points

- VM/page-cache vnode operations and helpers: `nfs4_getapage()` tail, `nfs4_readahead()`, `nfs4_putpage()`, `nfs4_putapage()`, `nfs4_sync_putapage()`, `nfs4_pageio()`, `nfs4_sync_pageio()`, and `nfs4_dispose()`.
- mmap operations: `nfs4_map()`, `open_and_get_osp()`, `nfs4_addmap()`, `nfs4_delmap()`, `nfs4_delmap_callback()`, plus delmap-caller list helpers.
- File/attribute operations: `nfs4_space()`, `nfs4_realvp()`, `nfs4_pathconf()`, `nfs4_setsecattr()`, `nfs4_getsecattr()`, and ACL mask/translation helpers.
- Cache/state helpers: `nfs4_update_attrcache()`, `nfs4_update_dircaches()`, `nfs4open_confirm()`, `state_to_cred()`, `nfs4_find_sysid()`, `vtodv()`, and `vtoname()`.
- Locking entry points and internals: `nfs4_frlock()`, `nfs4frlock()`, `nfs4_safelock()`, `nfs4_register_lock_locally()`, `nfs4_lockrelease()`, denial conversion helpers, and lost-lock reinstate helpers.
- Close-state entry points: `nfs4close_notw()`, `nfs4close_all()`, and `nfs4close_one()`.

## Core Control Flow

`nfs4_getapage()` completes page fault/page-in handling by computing block-sized or page-sized reads, queuing readahead when sequential access is detected, calling `pvn_read_kluster()`, issuing `nfs4_bio()` unless the request is known beyond EOF in `segkmap`, and returning pages through `pvn_plist_init()`.

`nfs4_putpage()` and `nfs4_putapage()` coordinate dirty-page writeback with `rp->r_count`, async I/O, and `R4MODINPROGRESS` protection so writes are not lost while `r_size` is unstable. COMMIT paths serialize through `R4COMMIT`, gather committable pages, issue `OP_COMMIT`, and repeat flush/commit when the server write verifier changes.

`nfs4_map()` validates cache/lock safety, creates missing open-stream state for mmap, then maps through `as_map()`. `nfs4_addmap()` updates rnode and open-stream mmap counters. `nfs4_delmap()` installs an address-space callback and returns `EAGAIN` so costly flush/CLOSE work runs without holding `as->a_lock`.

`nfs4_frlock()` validates POSIX locks, flushes pages before non-query operations, serializes against mmap, then delegates protocol work to `nfs4frlock()`. `nfs4frlock()` builds `PUTFH + LOCK/LOCKU/LOCKT` compounds, synchronizes open/lock seqids, handles delegation reopen, recovery, credential retry, denied blocking retries, local lock registration, and lost request preservation.

`nfs4close_one()` handles normal, delmap, force, resend, and after-resend close paths. It decrements open/mmap counters, performs `OPEN_DOWNGRADE` when references remain, skips OTW close for delegation-only or failed-reopen streams, sends final `CLOSE` when needed, and cleans up state references.

## State and Synchronization

- Rnode VM state uses `r_statelock`, `r_count`, `r_cv`, `r_flags`, `r_size`, `r_nextr`, `r_error`, `r_commit`, `r_mapcnt`, `r_inmap`, and `r_indelmap`.
- Commit state uses `R4COMMIT`, `R4COMMITWAIT`, `r_commit.c_cv`, `c_pages`, `c_commbase`, `c_commlen`, and page `p_fsdata` values `C_NOCOMMIT`, `C_DELAYCOMMIT`, and `C_COMMIT`.
- mmap/lock exclusion uses `r_lkserlock`, `r_rwlock`, `VNOCACHE`, remote-lock checks, mandatory-lock checks, and lost-lock conflict checks.
- NFSv4 open state uses open owners/streams, `os_sync_lock`, `os_open_ref_count`, `os_mapcnt`, `os_mmap_read`, `os_mmap_write`, `os_valid`, `os_force_close`, and `os_failed_reopen`.
- Lock state uses local `reclock()` with `LM_SYSID_CLIENT`, lock-owner seqids/stateids, `lo_pending_rqsts`, lost-request queues, and recovery synchronization.

## Dependencies

This chunk depends on illumos vnode, VM, page, segment, address-space callback, DNLC, lock manager, credential, signal, and zone APIs. It also depends on NFSv4 compound RPC operations including `OP_CPUTFH`, `OP_COMMIT`, `OP_OPEN_CONFIRM`, `OP_LOCK`, `OP_LOCKU`, `OP_LOCKT`, `OP_CLOSE`, and `OP_OPEN_DOWNGRADE`, plus recovery, delegation, ACL, and state-owner helpers elsewhere in the NFSv4 client.

## Risks and Edge Cases

- The `R4MODINPROGRESS`/`r_size` handshake prevents dirty-page write loss during extending writes.
- COMMIT must detect write-verifier changes and re-dirty/rewrite pages before acknowledging stability.
- `nfs4_delmap()` relies on callers interpreting `EAGAIN` as callback-driven retry, not ordinary failure.
- mmap and byte-range locks are conservative: mapped files only allow whole-file non-mandatory locks.
- Lost `LOCK`, `LOCKU`, and `CLOSE` requests treat timeout, `EINTR`, and forced unmount as possibly delivered server requests.
- `nfs4_create_getsecattr_return()` contains `if (!orig_mask & VSA_...)` expressions; precedence makes these `(!orig_mask) & ...`, which may not match the intended count-only cleanup checks.
- `nfs4close_one()` cleanup depends on many boolean ownership flags for locks, seqid syncs, stream refs, and start-fop state.

## Cross-Chunk References

- Earlier lines define vnode operation tables, `nfs4_getpage()`, `nfs4_putpages()`, `nfs4_bio()`, open/create/remove/rename paths, delegation helpers, and globals consumed here.
- `nfs4_getapage()` begins before this chunk; this chunk contains most of its body but not the signature setup.
- This chunk calls helpers defined elsewhere, including `nfs4_async_readahead()`, `nfs4_async_putapage()`, `nfs4_async_pageio()`, `nfs4_async_commit()`, `nfs4_rdwrlbn()`, `nfs4_flush_pages()`, `nfs4close_otw()`, and recovery/state-owner helpers.
- Recovery code in other files consumes lost-request records prepared here for `OP_LOCK`, `OP_LOCKU`, `OP_CLOSE`, and `OP_OPEN_DOWNGRADE`.
