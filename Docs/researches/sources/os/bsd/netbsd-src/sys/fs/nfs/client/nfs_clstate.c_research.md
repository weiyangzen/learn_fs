# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_clstate.c

## Purpose

Implements NetBSD/FreeBSD-derived NFSv4 client-side state management: client IDs, open owners, lock owners, opens, byte-range locks, delegations, callbacks, recovery, lease renewal, and pNFS layout/device state.

The file is the core NFSv4 state machine behind vnode open/close/lock paths and callback service behavior. It maintains in-kernel state that mirrors server-granted stateids and repairs or discards that state when the server reports stale, expired, or recalled state.

## Main Data Model

- Global client list: `nfsclhead`, protected by `NFSCLSTATEMUTEX`.
- Per-mount client state: `struct nfsclclient`, linked from `nfsmount::nm_clp`.
- Open owners: `struct nfsclowner`, keyed by POSIX process-derived owner bytes.
- Opens: `struct nfsclopen`, keyed by file handle under an open owner.
- Lock owners: `struct nfscllockowner`, keyed by lock owner bytes under an open.
- Byte locks: `struct nfscllock`, maintained as ordered, non-overlapping byte ranges.
- Delegations: `struct nfscldeleg`, hashed by file handle and LRU-tracked in `nfsc_deleg`.
- pNFS layouts: `struct nfscllayout`, hashed by MDS file handle and LRU-tracked.
- pNFS file layout segments: `struct nfsclflayout`, split by read/read-write layout lists.
- pNFS device info: `struct nfscldevinfo`, referenced by file layout entries.

The comments at the top define the design choice: open owners and lock owners map to POSIX process identity, trading extra owner structures for natural operation serialization.

## Key Entry Points

- `nfscl_open()` finds or creates an open owner/open, optionally using a delegation.
- `nfscl_deleg()` inserts or finds a delegation for a file handle.
- `nfscl_getstateid()` chooses a delegation, lock, open, or zero stateid for I/O.
- `nfscl_getcl()` finds/creates a clientid and performs SetClientID/session setup as needed.
- `nfscl_getbytelock()` prepares local/server byte-range lock state before LOCK RPCs.
- `nfscl_relbytelock()` updates local lock state before LOCKU RPCs.
- `nfscl_checkwritelocked()` checks whether local state says a process holds a write lock.
- `nfscl_getclose()` decrements open counts on close.
- `nfscl_doclose()` performs server CLOSEs later, usually during vnode inactive handling.
- `nfscl_docb()` handles NFSv4 callback compounds.
- `nfscl_renewthread()` renews leases and performs deferred cleanup, delegation return, layout return, and recovery.
- `nfscl_initiate_recovery()` marks a client for state recovery.
- `nfscl_hasexpired()` handles server-side state expiration.
- `nfscl_umount()` terminates renew state and tears down client state on unmount.
- `nfscl_layout()`, `nfscl_getlayout()`, `nfscl_adddevinfo()`, and `nfscl_layoutcommit()` maintain pNFS layout/device state.

## Open And Delegation Flow

`nfscl_open()` allocates possible owner/open objects before taking global state locks, avoiding sleeping allocation while mutating lists. It then:

1. Gets the NFSv4 client with `nfscl_getcl()`.
2. Builds an owner name from the current process.
3. Checks for a usable delegation if `usedeleg` is set.
4. Selects either delegation-local owner lists or normal client owner lists.
5. Calls `nfscl_newopen()` to insert missing owner/open state.
6. Marks whether an actual server OPEN is required via `NFSCLOPEN_DOOPEN`.

Delegation-local opens are tracked separately under the delegation and later migrated to server state when a delegation is recalled.

## Stateid Selection

`nfscl_getstateid()` prioritizes:

1. Valid delegation stateid for matching file and access mode.
2. Matching lock owner stateid, except for data-server I/O.
3. Matching open owner/open stateid.
4. Any open that satisfies the requested access mode.
5. Zero stateid for non-DS fallback when no open state is needed.

It waits while recovery is active, so I/O does not consume stale or transitional state.

## Clientid Lifecycle

`nfscl_getcl()` creates the per-mount client object and fills:

- owner list
- delegation queue/hash
- layout queue/hash
- device list
- callback identifier
- client identity bytes from host UUID plus mount-specific value

It then acquires an exclusive NFSv4 state lock if SetClientID/session setup is required. It retries transient `STALECLIENTID`, `BADSESSION`, `STALEDONTRECOVER`, and `CLIDINUSE` conditions. Existing client state uses reference counts instead of exclusive locking.

`nfscl_clientrelease()` and `nfscl_clrelease()` release either an exclusive lock or a reference, depending on current lock state.

## Byte-Range Locking

`nfscl_getbytelock()` creates lock owner and lock range objects, checks delegation-local eligibility, checks local conflicts, merges the requested lock into local state, and decides whether the server RPC is needed.

`nfscl_updatelock()` is the core interval-list algorithm. It keeps lock ranges sorted by offset, non-overlapping, and merged when possible. It handles:

- full absorption of existing ranges
- trimming front or back of an existing range
- splitting an existing range into two
- unlock ranges
- same-type contiguous/overlapping merge

`nfscl_localconflict()` and `nfscl_checkconflict()` detect conflicts from other owners when byte ranges overlap and at least one side is a write lock or the new operation is unlock-like.

## Cleanup, Expiry, And Recovery

`nfscl_cleanup_common()` marks open owners defunct after a process exits, or frees empty owners immediately. `nfscl_cleanupkext()` periodically scans for dead processes and empty lock owners, moving releasable lock owners to a temporary list for `ReleaseLockOwner`.

`nfscl_expireclient()` handles `NFSERR_EXPIRED`. It merges delegation-local opens back into normal client lists, discards delegation locks, tries to reopen state that has no unrecoverable locks/share-deny state, and frees unrecoverable opens.

`nfscl_recover()` handles stale clientid/stateid/session cases. It:

1. Exclusively locks client state and marks recovery in progress.
2. Drops all pNFS layouts.
3. Re-establishes the clientid/session.
4. Marks outstanding queued requests `R_DONTRECOVER`.
5. Marks delegations as needing reclaim.
6. Reclaims opens and then locks.
7. Reclaims standalone delegations by synthetic opens.
8. Closes extra opens and returns extra delegations.
9. Sends `RECLAIM_COMPLETE` for NFSv4.1+.
10. Clears recovery flags and wakes waiters.

## Renew Thread

`nfscl_renewthread()` is the background maintenance loop. It:

- renews the MDS lease and DS sessions
- triggers recovery when stale/bad session errors occur
- handles total recall when callback path is down
- frees defunct empty open owners
- processes delegation recalls
- trims old delegations over the high-water mark
- processes layout recalls and stale layouts
- sends layout commits before layout return when required
- frees unused pNFS device info
- returns cleaned/recalled delegations
- periodically releases lock owners for exited processes
- exits only after `NFSCLFLAGS_UMOUNT`

This makes the renew thread both the lease-renewal worker and deferred state garbage collector.

## Callback Handling

`nfscl_docb()` parses callback COMPOUND requests and implements:

- `CB_GETATTR`: returns delegated size/change attributes.
- `CB_RECALL`: marks matching delegations for recall and wakes the renew thread.
- `CB_LAYOUTRECALL`: marks matching pNFS layouts for recall by file, fsid, or all.
- `CB_SEQUENCE`: validates NFSv4.1 callback session sequencing and caches replies.

Unsupported or illegal callback ops are mapped through `nfscl_errmap()`, which restricts errors to protocol-allowed callback error sets.

## Delegation Return Paths

`nfscl_recalldeleg()` moves delegation-local state back to server state. For write delegations it flushes dirty vnode data before returning. It then:

- moves local opens to normal open-owner state with `nfscl_moveopen()`
- replays local byte-range locks with `nfscl_relock()`
- returns errors that should trigger recovery if stale/bad session state is encountered

`nfscl_removedeleg()` and `nfscl_renamedeleg()` are used by remove/rename paths to locate and return relevant delegations, waiting for outstanding delegation I/O and recalling local state first when necessary.

## pNFS Layout Handling

`nfscl_layout()` creates or updates a file layout, merges new file-layout extents into read or read-write lists, and returns a referenced layout.

`nfscl_getlayout()` finds a layout usable for a given offset. It returns either a shared referenced layout when a matching layout segment exists, or an exclusive layout lock when the caller must fetch more layout state.

`nfscl_layoutrecall()` records ordered layout recalls. It orders file recalls before fsid/all recalls and compares wrapping sequence IDs with `nfscl_seq()`.

`nfscl_layoutreturn()` issues `LAYOUTRETURN` for each recall entry. `nfscl_dolayoutcommit()` issues `LAYOUTCOMMIT` for written read-write layout ranges and disables future commits if the server returns `NFSERR_NOTSUPP`.

## Integration Points

This file depends heavily on:

- RPC helpers: `nfsrpc_setclient`, `nfsrpc_openrpc`, `nfsrpc_lock`, `nfsrpc_closerpc`, `nfsrpc_renew`, `nfsrpc_delegreturn`, `nfsrpc_layoutreturn`, `nfsrpc_layoutcommit`.
- vnode/nfsnode helpers: `nfscl_ngetreopen`, `ncl_flush`, `VTONFS`, `NFSTOV`.
- NFSv4 lock helpers: `nfsv4_lock`, `nfsv4_unlock`, `nfsv4_getref`, `nfsv4_relref`.
- mount state from `struct nfsmount`.
- global request queue `nfsd_reqq` for marking stale in-flight requests.
- NFS statistics counters in `nfsstatsv1`.

## Concurrency Notes

- Global state mutations use `NFSCLSTATEMUTEX`.
- Client state has a lock/reference object used for exclusive recovery/setup versus shared users.
- Open owner and lock owner rwlocks serialize operation sequences per owner.
- Delegation/layout I/O uses `nfslock_usecnt` plus `NFSV4LOCK_WANTED` sleeps.
- Several functions intentionally drop `NFSCLSTATEMUTEX` around RPCs and reacquire afterward.

## Risks And Edge Cases

- Many operations rely on correct lock dropping/reacquiring around RPCs; mistakes can cause stale pointers or state races.
- Recovery paths intentionally discard state if reclaim fails, meaning byte locks can be lost.
- `nfscl_updatelock()` is compact but subtle; off-by-one or inclusive/exclusive range assumptions are high risk.
- Delegation recall flush errors from the renew thread can defer recall completion.
- Callback compound parsing must maintain exact XDR cursor state.
- pNFS layout recall ordering depends on sequence wrap logic that the source itself notes as uncertain.
- Some diagnostics use `printf` and panic on invariants that “should never happen.”

## Verification Ideas

- Unit-style tests for `nfscl_updatelock()` interval merge/split/unlock behavior.
- Recovery tests covering stale clientid, bad session, expired state, and no-grace reclaim.
- Callback tests for illegal op/error mapping and `CB_SEQUENCE` reply cache behavior.
- Delegation recall tests with dirty write delegation data and local locks.
- pNFS layout recall/return tests for file/fsid/all recalls and sequence wrap ordering.
