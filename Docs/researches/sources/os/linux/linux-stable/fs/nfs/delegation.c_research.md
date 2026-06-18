# File Research: sources/os/linux/linux-stable/fs/nfs/delegation.c

## Purpose

`delegation.c` manages NFSv4 file and directory delegations. It tracks delegations per inode/server/client, validates and copies delegation stateids, handles delegation recall/return, supports reclaim after recovery, tests and removes expired delegations, limits delegation cache pressure with an LRU, and coordinates state recovery when delegations become invalid.

## Main Responsibilities

- Allocate, update, attach, detach, reference, and free `struct nfs_delegation`.
- Check whether an inode has a usable read/write/time delegation.
- Copy or refresh delegation stateids for NFS operations.
- Return delegations synchronously, asynchronously, on close, on eviction, or from state-manager queues.
- Reclaim open and lock state when returning regular-file delegations.
- Expire unused, unreferenced, or all delegations.
- Mark delegations revoked, returned, bad, needing reclaim, or needing expiry tests.
- Find delegated inodes by filehandle for callback recall.
- Reap unclaimed delegations after reboot recovery and test/free expired delegations after lease loss.
- Allocate the per-server delegation hash table.

## Key Functions

- `nfs_inode_set_delegation()` installs a new delegation or updates/replaces an existing one, handling duplicate delegation cases and write-delegation upgrades.
- `nfs_inode_reclaim_delegation()` updates an existing delegation during reclaim or installs a new one if absent.
- `nfs4_get_valid_delegation()`, `nfs4_have_delegation()`, and `nfs4_check_delegation()` validate delegation type and flags under RCU.
- `nfs_async_inode_return_delegation()` marks a matching delegation for state-manager return and breaks local leases nonblocking.
- `nfs4_inode_return_delegation()` flushes data and returns a delegation synchronously.
- `nfs4_inode_set_return_delegation_on_close()` and `nfs4_inode_return_delegation_on_close()` defer returns until the last open closes when possible.
- `nfs_end_delegation_return()` breaks leases, reclaims opens/locks as needed, waits for recovery when synchronous, and sends `DELEGRETURN`.
- `nfs_client_return_marked_delegations()` is the state-manager entry for processing return queues across all client servers.
- `nfs_delegation_find_inode()` searches per-server delegation hash tables by filehandle for callback recall.
- `nfs_remove_bad_delegation()`, `nfs_delegation_mark_returned()`, and `nfs_revoke_delegation()` handle server-reported invalid delegation stateids.
- `nfs_delegation_mark_reclaim()` and `nfs_delegation_reap_unclaimed()` support reboot recovery.
- `nfs_test_expired_all_delegations()` and `nfs_reap_expired_delegations()` drive TEST/FREE_STATEID style expiry validation.
- `nfs4_copy_delegation_stateid()` and `nfs4_refresh_delegation_stateid()` provide stateid access for other NFS operations.
- `nfs4_delegation_hash_alloc()` sizes and initializes the delegation hash table from the delegation watermark.

## Control Flow and State

Delegations are visible through three structures: an RCU pointer on `nfs_inode`, a per-server `delegations` list, and a per-server filehandle hash table. A separate `entry` list node moves delegations through return, LRU, and delayed-return queues. Active delegation count is tracked by `server->nr_active_delegations`.

The main flags are `NEED_RECLAIM`, `RETURN_IF_CLOSED`, `REFERENCED`, `RETURNING`, `REVOKED`, `TEST_EXPIRED`, and `DELEGTIME`. `RETURNING` serializes return attempts. `REVOKED` invalidates local use and decrements active count. `REFERENCED` drives LRU eviction passes. `TEST_EXPIRED` drives lease-loss validation.

Delegation return for regular files can require breaking local leases, reclaiming opens, and reclaiming locks before issuing `DELEGRETURN`. If nonblocking return hits recovery or reclaim delay, the delegation is moved to delayed/return queues and the state manager retries later.

## Integration Points

- Callback recall in `callback_proc.c` calls `nfs_delegation_find_inode()` and `nfs_async_inode_return_delegation()`.
- Callback getattr uses `nfs4_get_valid_delegation()` and delegation `change_attr`.
- NFS open/lock recovery hooks are called through `nfs4_open_delegation_recall()` and `nfs4_lock_delegation_recall()`.
- Delegation return RPCs use `nfs4_proc_delegreturn()`.
- State-manager scheduling uses `NFS4CLNT_DELEGRETURN`, delayed return flags, reclaim flags, and expiry flags on `nfs_client`.
- Attribute helpers update delegated atime/mtime through declarations in `delegation.h`.

## Concurrency and Lifetime

The code combines RCU for fast delegation lookup, `clp->cl_lock` for attach/detach against inode pointers and hash/list membership, `server->delegations_lock` for queue/LRU movement, per-delegation spinlocks for mutable fields, and refcounts for delegation lifetime. Freed delegations are released with `kfree_rcu()`. Inode references are acquired with `igrab()` before operations that leave RCU protection.

## Risks and Edge Cases

- Duplicate delegations from broken servers are tolerated only for write upgrades; otherwise the new delegation is discarded or the old one is returned.
- Directory delegations can be globally disabled by the `directory_delegations` module parameter, causing return-on-close behavior.
- Nonblocking delegation return can delay and set `NFS4CLNT_DELEGRETURN_DELAYED`; the state manager sleeps briefly to avoid hard loops.
- Expiry testing can be interrupted by server reboot/session reset and requeues work with `-EAGAIN`.
- The delegation hash bucket count is based on `nfs_delegation_watermark / 16`; very small configured watermarks should be reviewed for hash sizing behavior.

## Testing Focus

Test new delegation install, in-place stateid update, duplicate delegation rejection/upgrade, return-on-close with open-file list transitions, recall while state recovery is active, lock/open reclaim failures, LRU over-watermark returns, revoke/returned stateid paths, filehandle lookup under unmount races, reclaim marking/reaping, expired delegation testing, stateid copy/refresh, and directory delegation disabled behavior.
