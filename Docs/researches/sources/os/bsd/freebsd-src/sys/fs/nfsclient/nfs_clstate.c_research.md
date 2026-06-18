# File Research: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_clstate.c

## Summary
Implements FreeBSD NFSv4 client state management: client IDs, sessions, open owners, opens, byte-range locks, delegations, callback handling, recovery, renewals, and pNFS layouts/device information.

## Main Responsibilities
- Creates and references per-mount `nfsclclient` state and performs SetClientID/CreateSession setup.
- Tracks NFSv4 open owners and open stateids, including pid-based and single-open-owner modes.
- Tracks lock owners and normalized non-overlapping byte-range lock lists.
- Supports read/write delegations, local opens/locks under delegations, delegation recall, and delegation return.
- Runs the renew thread for lease renewal, recovery, cleanup of exited process owners, delegation recall, layout recall, stale layout return, and data-server renewals.
- Handles NFSv4 callback compound operations such as CB_GETATTR, CB_RECALL, CB_SEQUENCE, CB_LAYOUTRECALL, CB_RECALL_SLOT, and CB_RECALL_ANY.
- Manages pNFS file/flexfile layouts, layout recalls, layout returns, layout commits, device-info references, and data-server error shutdown.

## Key APIs
- Client/open state: `nfscl_getcl()`, `nfscl_findcl()`, `nfscl_clientrelease()`, `nfscl_open()`, `nfscl_getstateid()`, `nfscl_getclose()`, `nfscl_doclose()`.
- Lock state: `nfscl_getbytelock()`, `nfscl_relbytelock()`, `nfscl_releasealllocks()`, `nfscl_checkwritelocked()`, `nfscl_lockrelease()`, `nfscl_lockt()`.
- Delegations: `nfscl_deleg()`, `nfscl_delegreturnvp()`, `nfscl_trydelegreturn()`, `nfscl_mustflush()`, `nfscl_nodeleg()`, `nfscl_removedeleg()`, `nfscl_renamedeleg()`, `nfscl_startdelegrecall()`.
- Recovery/renewal: `nfscl_renewthread()`, `nfscl_initiate_recovery()`, `nfscl_hasexpired()`, `nfscl_umount()`.
- Callback path: `nfscl_docb()`.
- pNFS: `nfscl_layout()`, `nfscl_getlayout()`, `nfscl_rellayout()`, `nfscl_adddevinfo()`, `nfscl_getdevinfo()`, `nfscl_reldevinfo()`, `nfscl_freelayout()`, `nfscl_layoutcommit()`, `nfscl_dserr()`, `nfscl_cancelreqs()`.

## Important Behavior
Open owners normally map to POSIX process identity; NFSv4.1/4.2 mounts with the single-open-owner option can use one all-zero open owner and shared owner locking for concurrent opens. Opens are delayed for server-side CLOSE until vnode inactive/close processing because mmap and inherited descriptors make a syscall close hard to map to one exact NFS open.

Lock owners map to POSIX/flock identities. `nfscl_updatelock()` maintains ordered, merged, non-overlapping local byte-range lock ranges and handles unlock splits. Delegations allow local opens and locks when safe; recall migrates local delegation opens/locks to server state and flushes dirty data for write delegations.

Recovery serializes on the client sleep lock, reestablishes client/session state, marks queued requests `R_DONTRECOVER`, reclaims opens, locks, and delegations where possible, expires unrecoverable state, and issues `RECLAIM_COMPLETE` for NFSv4.1+. The renew thread also performs periodic lease renewals, callback-path-down total recalls, exited-process cleanup, stale delegation/layout trimming, layout returns, layout commits, and DS session renewals.

`nfscl_docb()` builds callback replies and validates callback sequencing for NFSv4.1+. It can return delegation attributes, mark delegations for recall, process layout recalls by file/fsid/all, reduce callback slot counts, adjust delegation/layout high-water marks, and cache callback replies by session slot.

## State and Synchronization
Global state is protected by `NFSCLSTATEMUTEX`; client structures also use `nfsv4_lock` reference/exclusive-lock fields. State is arranged in client lists, open-owner lists, file-handle hash tables, delegation hash/LRU lists, lock-owner lists, layout hash/LRU lists, recall lists, and device-info lists. Many paths intentionally allocate before taking mutexes to avoid sleeping while list state is locked.

## pNFS Details
Layouts are stored by MDS file handle and split into read/RW file-layout lists. Layout recalls are ordered by recall type and wrapped seqid comparison. Layout returns can carry data-server error/device information. Device info objects are reference-counted by live users and layout references; unused entries are freed by the renew thread. Flexfile layouts can suppress layoutcommit via server flags.

## Risks
This is high-risk concurrency code: client recovery, unmount, forced dismount, callback threads, renew thread, vnode reclaim, close, delegation recall, and pNFS I/O can all interact. Correctness depends on strict lock/refcount discipline, careful avoidance of sleeping under the wrong mutex, stateid seqid handling, list/hash consistency, and cleanup of defunct owners. Error handling can intentionally discard unrecoverable lock/delegation/layout state, so callers must tolerate lost state after server expiry or failed reclaim.
