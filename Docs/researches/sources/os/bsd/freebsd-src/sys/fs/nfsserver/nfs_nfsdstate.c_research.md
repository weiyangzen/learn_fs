# File Research: sources/os/bsd/freebsd-src/sys/fs/nfsserver/nfs_nfsdstate.c

## Purpose

`nfs_nfsdstate.c` is the FreeBSD NFS server's central NFSv4 state-management implementation. It owns client IDs, sessions, open owners, open stateids, lock owners, byte-range locks, delegations, grace/reclaim stable storage, callback RPCs, and pNFS layout/device state.

This file is not a filesystem implementation by itself. It is the state engine that lets the NFS server enforce NFSv4 protocol semantics over vnode-backed files.

## Major Responsibilities

- NFSv4 client lifecycle:
  - `nfsrv_setclient()`
  - `nfsrv_getclient()`
  - `nfsrv_destroyclient()`
  - `nfsrv_adminrevoke()`
  - `nfsrv_zapclient()`
- NFSv4 open/close/share state:
  - `nfsrv_opencheck()`
  - `nfsrv_openctrl()`
  - `nfsrv_openupdate()`
- NFSv4 byte-range locking:
  - `nfsrv_lockctrl()`
  - `nfsrv_releaselckown()`
  - `nfsrv_updatelock()`
  - local VOP advisory lock integration through `nfsrv_locallock()`
- Delegations and callbacks:
  - `nfsrv_issuedelegation()`
  - `nfsrv_delegupdate()`
  - `nfsrv_delegconflict()`
  - `nfsrv_docallback()`
  - `nfsd_recalldelegation()`
  - `nfsd_disabledelegation()`
- NFSv4.1 sessions:
  - `nfsrv_checksequence()`
  - `nfsrv_destroysession()`
  - `nfsrv_bindconnsess()`
  - `nfsrv_freesession()`
  - `nfsrv_cache_session()`
- Grace period and stable storage:
  - `nfsrv_setupstable()`
  - `nfsrv_updatestable()`
  - `nfsrv_writestable()`
  - `nfsrv_checkgrace()`
  - `nfsrv_checkstable()`
- pNFS layout/device management:
  - `nfsrv_layoutget()`
  - `nfsrv_layoutreturn()`
  - `nfsrv_layoutcommit()`
  - `nfsrv_getdevinfo()`
  - `nfsrv_createdevids()`
  - `nfsrv_copymr()`
  - `nfsrv_mdscopymr()`
  - `nfsrv_marknospc()`

## Core State Model

The file maintains these state groupings:

- Client hash table: `VNET(nfsclienthash)`
- File-handle lock hash table: `VNET(nfslockhash)`
- Session hash table: `VNET(nfssessionhash)`
- pNFS layout hash table: `nfslayouthash`
- Stable-storage reclaim list: `VNET(nfsrv_stablefirst).nsf_head`
- Device ID list: `nfsrv_devidhead`
- pNFS recall/don't-layout lists:
  - `nfsrv_recalllisthead`
  - `nfsrv_dontlisthead`

The state hierarchy is roughly:

`nfsclient` -> open owners -> opens -> lock owners -> locks

File-centered state is tracked by `nfslockfile`, keyed by vnode file handle, with lists for opens, locks, delegations, local lock mirrors, and rollback records.

## Important Tunables and Counters

The file defines NFS server sysctls for hash sizes and state limits:

- `vfs.nfsd.statehashsize`
- `vfs.nfsd.clienthashsize`
- `vfs.nfsd.fhhashsize`
- `vfs.nfsd.sessionhashsize`
- `vfs.nfsd.layouthighwater`
- `vfs.nfsd.v4statelimit`
- `vfs.nfsd.writedelegifpos`
- `vfs.nfsd.allowreadforwriteopen`
- `vfs.nfsd.pnfsstrictatime`
- `vfs.nfsd.flexlinuxhack`
- `vfs.nfsd.testing_disable_grace`

Important global counters include:

- `nfsrv_openpluslock`: total open-owner/open/lock-owner/lock/delegation-like state pressure
- `nfsrv_delegatecnt`: delegation count
- `nfsrv_writedelegcnt`: active write delegation count
- `nfsrv_clients`: client count
- `nfsrv_layoutcnt`: layout count
- `nfsrv_devidcnt`: pNFS device count

## Locking and Concurrency

The file uses several lock layers:

- `NFSLOCKSTATE()` protects most NFSv4 state lists and counters.
- `nfsv4rootfs_lock` acts as an exclusive quiescing lock to block other nfsd threads while expiring clients, revoking state, or rewriting state that can sleep.
- Per-session hash locks protect session lookup and slot state.
- Layout hash locks protect pNFS layout lists.
- Device, recall, and don't-list mutexes protect pNFS auxiliary lists.

A recurring pattern is:

1. Take the state lock for ordinary list inspection.
2. If a conflict requires sleeping, callbacks, stable-storage writes, or client revocation, drop locks or acquire `nfsv4rootfs_lock`.
3. Return retry markers such as `-1` or `1` so the caller can rescan after state may have changed.

This pattern is central to `nfsrv_lockctrl()`, `nfsrv_opencheck()`, `nfsrv_openctrl()`, `nfsrv_clientconflict()`, and `nfsrv_delegconflict()`.

## Client Lifecycle

`nfsrv_setclient()` handles SetClientID/ExchangeID-style client registration. It searches for an existing client owner string, handles verifier changes as client reboot, assigns client IDs based on `nfsrvboottime` plus a generated index, and preserves or discards old state depending on confirmation semantics.

`nfsrv_getclient()` validates client IDs, confirms clients, creates NFSv4.1 sessions, handles backchannel setup, renews leases, checks credential ownership, and rejects revoked or stale clients.

`nfsrv_destroyclient()` removes an NFSv4.1 client ID only if it has no sessions, delegations, or stateids. `nfsrv_adminrevoke()` writes a stable-storage revoke record, marks the client admin-revoked, and clears its state.

## Open and Share State

`nfsrv_opencheck()` performs pre-open validation: restart/grace checks, resource limit checks, open-owner sequence validation, lockfile lookup, share-deny conflict checks, and delegation conflict recalls.

`nfsrv_openctrl()` mutates state after open succeeds. It creates or updates open owners and open stateids, handles reclaim, `CLAIM_DELEGATE_PREV`, `CLAIM_DELEGATE_CUR`, open confirmation requirements, and delegation issuance. For NFSv4.1 clients, first state acquisition can stamp stable storage without OpenConfirm.

`nfsrv_openupdate()` handles OpenConfirm, Close, and OpenDowngrade. Close frees open state and, when local locking is enabled, coordinates vnode unlock/relock around local advisory lock cleanup.

## Lock State

`nfsrv_lockctrl()` is the main byte-range lock engine. It supports:

- lock test
- lock acquire
- unlock
- open-to-lock-owner conversion
- stateid validation
- share access checks
- delegation conflict checks
- range conflict reporting
- local advisory lock rollback/commit

`nfsrv_updatelock()` maintains non-overlapping ordered ranges per lock owner, merging, trimming, splitting, or deleting ranges for lock/unlock requests. It is also reused for local lock mirror state.

When `nfsrv_dolocallocks` is enabled, NFSv4 locks are reflected into local vnode advisory locks through `nfsvno_advlock()`. The rollback list in `nfslockfile` makes failed multi-range updates reversible.

## Delegations and Callbacks

Delegations are stored as `nfsstate` entries linked to the client, state hash, and file lockfile. `nfsrv_issuedelegation()` decides whether read or write delegations can be issued, records why delegation was not granted in open result flags, and supports read-to-write delegation upgrade.

`nfsrv_delegconflict()` recalls conflicting delegations with `CB_RECALL`, waits or returns `NFSERR_DELAY`, expires old delegations after timeout, and writes revoke records when needed.

`nfsrv_docallback()` builds and sends callback RPCs for:

- `CB_NULL`
- `CB_GETATTR`
- `CB_RECALL`
- `CB_LAYOUTRECALL`

For NFSv4.1+, callbacks use backchannel sessions and `CB_SEQUENCE`.

## Grace and Stable Storage

The stable-storage subsystem records previous boot times and per-client state/revoke records. Its role is to decide which clients may reclaim state after server restart.

- `nfsrv_setupstable()` reads the stable file, sets `nfsrvboottime`, reconstructs reclaim eligibility, and starts grace if the file is valid.
- `nfsrv_updatestable()` rewrites stable storage at end of grace and writes records for clients that reclaimed state.
- `nfsrv_writestable()` appends client state or revoke records.
- `nfsrv_checkgrace()` enforces reclaim-only behavior during grace and no-reclaim behavior after grace.
- `nfsrv_markstable()` and `nfsrv_markreclaim()` update reclaim tracking.

If stable storage is corrupt or unavailable, the code ends grace early and denies reclaim.

## Session Handling

NFSv4.1 session state is keyed by session ID and stores slot/reply-cache information. `nfsrv_checksequence()` validates sequence IDs, renews the client lease, records implied client ID, sets machine-credential allowed operations, and reports callback-path status.

`nfsrv_cache_session()` saves replies into session slots. `nfsrv_destroysession()` and `nfsrv_freesession()` remove sessions while guarding against busy backchannels. `nfsrv_bindconnsess()` attaches a connection as forechannel/backchannel and updates callback transport state.

## pNFS Layouts and Devices

The pNFS portion supports file layouts and flexible file layouts.

`nfsrv_layoutget()` validates layout requests, normalizes whole-file layout ranges, checks readonly exports and no-layout lists, reuses existing layout state, or builds a new layout from DS file handles and device IDs.

`nfsrv_filelayout()` emits RFC5661 file-layout XDR. `nfsrv_flexlayout()` emits flexible-file-layout XDR, including mirrors, stripes, synthetic owner IDs, and a Linux compatibility hack controlled by `nfsrv_flexlinuxhack`.

`nfsrv_layoutreturn()` processes file/fsid/all layout returns, updates MDS attributes, frees matching layouts, wakes recall waiters, and parses flex layout errors.

Device management functions create, delete, disable, and report pNFS device IDs:

- `nfsrv_createdevids()`
- `nfsrv_setdsserver()`
- `nfsrv_allocdevid()`
- `nfsrv_getdevinfo()`
- `nfsrv_deldsserver()`
- `nfsrv_deldsnmp()`
- `nfsrv_delds()`
- `nfsrv_freealllayoutsanddevids()`

## pNFS Mirror Recovery

`nfsrv_copymr()` coordinates recovery of a mirrored DS file. It disables RW layout issuance for the MDS file, recalls outstanding RW layouts, waits for returns, locks the MDS vnode, creates the new DS file, copies data while preserving holes where possible, copies ACLs when supported, syncs, sets modify time, updates the `pnfsd.dsfile` extended attribute, and re-enables layouts.

`nfsrv_mdscopymr()` prepares mirror copy/recovery by resolving MDS and DS paths, validating NFS mounts, finding device structures, reading DS metadata from extended attributes, and selecting the source DS file.

## External Integration Points

This file depends heavily on:

- vnode operations:
  - `nfsvno_getfh()`
  - `nfsvno_setattr()`
  - `nfsvno_advlock()`
  - `nfsvno_updfilerev()`
  - `VOP_GETATTR`, `VOP_SETATTR`, `VOP_GETACL`, `VOP_SETACL`, `VOP_FSYNC`
- RPC/backchannel APIs:
  - `newnfs_connect()`
  - `newnfs_request()`
  - `clnt_bck_create()`
  - `SVC_ACQUIRE` / `SVC_RELEASE`
- NFS reply cache/session helpers:
  - `nfsv4_seqsession()`
  - `nfsv4_seqsess_cacherep()`
  - `nfsv4_sequencelookup()`
- pNFS DS helpers declared elsewhere:
  - `nfsrv_dsgetdevandfh()`
  - `nfsrv_dsgetsockmnt()`
  - `nfsrv_dscreate()`
  - `nfsrv_killrpcs()`
  - `nfsrv_updatemdsattr()`

## Error Semantics

The code maps protocol conditions to NFSv4 errors carefully:

- stale client/server boot mismatch:
  - `NFSERR_STALECLIENTID`
  - `NFSERR_STALESTATEID`
- bad or old state:
  - `NFSERR_BADSTATEID`
  - `NFSERR_OLDSTATEID`
  - `NFSERR_BADSEQID`
- grace/reclaim:
  - `NFSERR_GRACE`
  - `NFSERR_NOGRACE`
  - `NFSERR_RECLAIMCONFLICT`
- sharing and locking:
  - `NFSERR_SHAREDENIED`
  - `NFSERR_LOCKED`
  - `NFSERR_DENIED`
  - `NFSERR_LOCKSHELD`
  - `NFSERR_OPENMODE`
- callback/session:
  - `NFSERR_CBPATHDOWN`
  - `NFSERR_BADSESSION`
  - `NFSERR_BACKCHANBUSY`
- pNFS:
  - `NFSERR_UNKNLAYOUTTYPE`
  - `NFSERR_LAYOUTTRYLATER`
  - `NFSERR_NOMATCHLAYOUT`
  - `NFSERR_TOOSMALL`
  - `NFSERR_NOSPC`

## Notable Implementation Details

- State IDs encode server boot time, client index, and per-client state index in `other[0..2]`.
- NFSv4.1 ignores open/lock seqids, but still uses session sequencing.
- NFSv4.1 stateid seqid `0` has special handling in several paths.
- All-zeros and all-ones stateids are special-cased for some I/O and setattr checks.
- Expired clients are not immediately removed by the timer; the timer marks them and an nfsd later performs stateful cleanup.
- Delegation recall intentionally avoids truncation recall semantics because vnode operation success cannot be guaranteed.
- Stable storage append records are chronological, so later state records override earlier revoke records.
- pNFS layout recalls increment layout stateid sequence before callback.
- Mirror recovery leaves unrecoverable recalled layouts on the recall list until nfsd restart if clients never return them, preferring safety over copying with outstanding RW layouts.

## Research Notes

This file is a high-risk concurrency and protocol-correctness component. Changes here should be tested against NFSv4.0 and NFSv4.1/4.2 separately, especially around:

- lease expiry and grace transitions
- callback path failures
- open-owner replay and seqid handling
- lock range merge/split behavior
- local advisory lock rollback
- session slot replay cache behavior
- delegation recall races
- pNFS layout return and mirror recovery
