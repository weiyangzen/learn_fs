# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_synchro.c

## Purpose
Implements HAMMER2 cluster synchronization threads. Each relevant PFS cluster node can have a management thread responsible for synchronizing that node from authoritative peer data.

## Thread Loop
`hammer2_primary_sync_thread()` handles stop, freeze, unfreeze, and remaster flags, then repeatedly runs synchronization from `pmp->iroot`. It wraps scans in a transaction, uses a deferred inode list for recursion, retries on `HAMMER2_ERROR_EAGAIN`, and sleeps for events or a five-second poll interval.

Single-node masters generally do not need these threads; multi-node masters, soft masters, slaves, copies, and other clustered PFS types do.

## Synchronization Scan
`hammer2_sync_slaves()` first collects authoritative cluster focus excluding the local index. If the local chain modify TID already matches the focus, it returns. Otherwise it scans authoritative children and local children in key order, comparing with `hammer2_chain_cmp()`:
- local extra item: `hammer2_sync_destroy()`
- same key but stale modify TID: `hammer2_sync_replace()`
- missing local item: `hammer2_sync_insert()`
- exact match: advance both scans

Inode children are deferred instead of recursed immediately because the XOP scan is still active across node threads. The function later updates the inode metadata/modify TID only after child synchronization succeeds.

## Insert/Delete/Replace
`hammer2_sync_insert()` upgrades parent locking, reissues lookup for insertion position, creates a chain matching the focus blockref, copies body data where needed, sets checks, and returns to shared locks.

`hammer2_sync_destroy()` upgrades parent and child locks, permanently deletes the local chain, then resumes iteration from the next key.

`hammer2_sync_replace()` locks the local chain exclusively, resizes if needed, modifies it, copies focus metadata and data, recalculates checks, and handles PFSROOT inode replacement specially so local distinguishing fields are preserved while common metadata is updated.

## Risk Notes
The file is dominated by careful lock ordering. Insert/delete/replace intentionally unlock and relock parent/child chains to avoid deadlocks. Synchronization is possible only when peer data can be collected authoritatively; mismatch/no-quorum conditions surface as HAMMER2 errors and may require retry or manual repair.
