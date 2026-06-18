# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_client_state.c

## Purpose
NFSv4 client-side state owner and stateid management. This file maintains open owners, open streams, lock owners, seqid synchronization, stateid selection, open downgrade behavior, and lost OPEN resend logic.

## Global Stateids
Defines the special all-zero stateid `clnt_special0` and all-ones stateid `clnt_special1`, used by NFSv4 protocol paths that need special stateid values.

## Open Owner Management
Open owners are keyed by credentials in per-mount hash buckets:
- `lock_bucket()` hashes effective plus real uid into `mi_oo_list` and locks the bucket.
- `find_open_owner_nolock()` searches active owners, reactivates valid-but-zero-ref owners, lazily moves invalid owners to the freed-owner list, and falls back to `find_freed_open_owner()`.
- `find_open_owner()` wraps this under `mi_lock`.
- `create_open_owner()` allocates an owner, holds credentials, initializes seqid state, assigns a unique `oo_name`, and inserts it in the credential hash.
- `open_owner_hold()` and `open_owner_rele()` manage references. Zero refs mark the owner invalid but defer actual destruction/list movement to later lookup paths.
- `nfs4_free_open_owner()` maintains the mount’s LRU-ish freed open-owner cache, bounded by `mi_foo_max`.
- `nfs4_destroy_open_owner()` releases credentials and synchronization primitives.

This lazy-free approach keeps locking simpler while avoiding immediate churn for credentials that may reopen soon.

## Open Stream Management
Open streams represent a specific open owner’s open state for an rnode:
- `find_open_stream()` searches `rp->r_open_streams`, returns with `os_sync_lock` held, and increments the refcount.
- `create_open_stream()` allocates a stream, initializes share counters/stateid/delegation flags, holds the open owner, inserts into the rnode stream list, and returns locked.
- `find_or_create_open_stream()` requires open seqid synchronization and either bumps `os_open_ref_count` or creates a stream.
- `open_stream_hold()`/`open_stream_rele()` manage stream references and remove/free the stream on last reference.
- `nfs4_clear_open_streams()` removes all streams from an rnode and releases their open owners.

## Lock Owner Management
Lock owners are tracked per-rnode by pid:
- `find_lock_owner()` searches the rnode lock-owner list and optionally requires a valid server stateid.
- `create_lock_owner()` allocates a lock owner, gives it list and caller refs, assigns a unique lock owner name containing sequence number plus pid, inserts it in the rnode list, and returns with `lo_lock` held.
- `nfs4_rnode_remove_lock_owner()` removes a lock owner from the rnode list and releases the list reference.
- `nfs4_flush_lock_owners()` removes all lock owners from an rnode.
- `lock_owner_hold()`/`lock_owner_rele()` manage lifetime; last release asserts the owner is off-list and no seqid is in use, then destroys it.
- `nfs4_setlockowner_args()` fills protocol lock-owner arguments from an existing valid lock owner or makes up a new owner value for test-style operations.

## Seqid Synchronization
NFSv4 open/lock sequence ids are serialized per owner:
- `nfs4_start_open_seqid_sync()` waits on `oo_cv_seqid_sync` until no open seqid is in use, but returns `EAGAIN` if recovery is active and the caller is not the recovery thread.
- `nfs4_end_open_seqid_sync()` clears in-use state and signals waiters.
- `nfs4_start_lock_seqid_sync()` performs equivalent serialization for lock owners, records `lo_seqid_holder`, and detects recovery interference.
- `nfs4_end_lock_seqid_sync()` clears `NFS4_LOCK_SEQID_INUSE`, resets holder, and signals waiters.
- `nfs4_get_open_seqid()`, `nfs4_set_open_seqid()`, `nfs4_get_and_set_next_open_seqid()`, `nfs4_set_lock_seqid()`, and `nfs4_set_lock_stateid()` update protocol seqid/stateid fields under the required synchronization assumptions.

Debug builds include optional seqid fault injection.

## Stateid Selection
Stateid priority is:
1. delegation stateid when valid for the operation
2. lock stateid for the pid
3. open stateid for the credential/rnode
4. special zero stateid

Functions:
- `nfs4_get_deleg_stateid()`
- `nfs4_get_lock_stateid()`
- `nfs4_get_open_stateid()`
- `nfs4_get_w_stateid()` for write paths
- `nfs4_get_stateid()` for read/setattr paths, with async-read retry support that skips already-tried stateid classes
- `nfs4_init_stateid_types()` initializes retry tracking.
- `nfs4_save_stateid()` records a failed stateid in the appropriate slot so retries can skip it.

## Open Bypass And Delegations
`nfs4_is_otw_open_necessary()` decides whether an OPEN must go over the wire:
- If an existing open stream already has sufficient access/deny state, it increments local counters and bypasses OTW OPEN.
- If a delegation is held, it may create an open stream locally using the delegation stateid, provided requested access is covered.
- It refuses bypass when an open stream failed reopen or when delegation/access conditions are insufficient.
- On delegation bypass with state tracking, it increments server state refcount.

`get_dtype()` safely reads current delegation type while respecting pending delegation return.

## Lock Argument Setup
`nfs4_setup_lock_args()` fills `locker4` for `LOCK`:
- For a new lock owner, it embeds open-owner seqid + open stateid + initial lock seqid + clientid/owner.
- For an existing lock owner, it sends lock stateid and next lock seqid.

`nfs4_find_or_create_lock_owner()` returns a referenced lock owner with lock seqid synchronization started. For new lock owners it also finds the corresponding open owner/open stream and starts open seqid synchronization. Failure paths clean up temporary lock owners and references, returning protocol-style `NFS4ERR_DELAY` or `NFS4ERR_IO`.

## Credentials For Over-The-Wire Calls
`nfs4_get_otw_cred()` returns an owner-specific over-the-wire credential if present, otherwise the supplied cred, with a hold.

`nfs4_get_otw_cred_by_osp()` iterates valid open streams for an rnode to find an alternate over-the-wire credential, optimized to try the caller’s credential first.

## BAD_SEQID And Lost Requests
`nfs4_create_bseqid_entry()` packages owner/vnode/pid/tag/seqid data for BAD_SEQID recovery.

`nfs4open_dg_save_lost_rqst()` records a lost `OPEN_DOWNGRADE` request when the downgrade call returns timeout, interrupt, or forced-unmount style errors.

## OPEN_DOWNGRADE
`nfs4_open_downgrade()` performs the protocol downgrade when local close/share counts imply reduced access:
- Computes new share access/deny bits.
- Skips OTW downgrade when no downgrade is needed and just decrements local counters.
- Sends `{ CPUTFH, GETATTR, OPEN_DOWNGRADE }`.
- Bumps open seqid when required by response semantics.
- Retries with the original credential on access failure if an alternate OTW credential was used.
- Saves recovery credential/seqid when recovery is needed.
- Updates the open stateid, stream counters, downgrade access, and attribute cache on success.

## Lost OPEN Resend
`nfs4_resend_open_otw()` resends a previously lost OPEN during recovery, then repairs local state:
- Handles normal reopen and `CLAIM_DELEGATE_CUR`.
- Uses non-create OPEN even if the original lost request created a file, because the goal is to clean up possible server-side state.
- Starts open seqid synchronization and sends `{ CPUTFH, COPEN, GETFH, GETATTR }`.
- Creates a vnode if needed from the returned filehandle/attributes.
- On reopen, verifies the returned filehandle or fileid matches the original; persistent or no-expire-with-open mismatches fail recovery.
- Updates volatile filehandles when acceptable.
- Performs OPEN_CONFIRM if required.
- Finds or creates open streams, updates stateid/share counters/delegation state, accepts delegations, caches or purges attributes, and releases seqid synchronization.

## Important Invariants
- Callers must respect lock ordering among `mi_lock`, open-owner bucket locks, rnode stream locks, owner locks, and seqid condition variables.
- Open and lock seqid synchronization must bracket any operation using or modifying owner seqids.
- Open streams can outlive local opens while references, mmap state, pending close, or recovery work exist.
- Delegation bypass must still create enough local state for later close/recovery accounting.
- Lost request handling assumes FIFO saved lost requests and one operation over the wire per seqid.
