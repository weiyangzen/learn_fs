# File Research: sources/os/linux/linux/fs/jbd2/transaction.c

## Role

`transaction.c` implements the JBD2 transaction and handle state machine. It creates running transactions, attaches filesystem update handles, accounts journal credits and revoke credits, manages write/create/undo access for metadata buffers, marks metadata dirty, forgets or invalidates buffers, handles transaction barriers, and tracks ordered-data inode ranges.

## Transaction and Handle Lifecycle

- `jbd2_get_transaction()` initializes a new `transaction_t`, assigns a TID, sets expiry, initializes counters, and installs the commit timer.
- `jbd2__journal_start()` / `jbd2_journal_start()` allocate handles, optional reserved handles, and attach them to a running transaction.
- `start_this_handle()` handles transaction creation, barrier waiting, reserved-handle conversion, journal-space waiting, credit accounting, and `memalloc_nofs_save()`.
- `jbd2_journal_stop()` drops the handle, optionally batches synchronous writers, requests commits for sync/expired transactions, waits for sync commits, releases credits, and frees reserved handles.
- `jbd2__journal_restart()` detaches a long-running operation from one transaction, requests commit, and reattaches to a new transaction with fresh credits.

## Credit and Space Accounting

The file enforces transaction size and log-space constraints with:
- `add_transaction_credits()`
- `jbd2_journal_extend()`
- `sub_reserved_credits()`
- `jbd2_max_user_trans_buffers()`

It limits user payload to the journal’s maximum transaction buffers minus descriptor/commit overhead, limits reserved credits to half a transaction, and waits for checkpoint space before dirtying buffers that could later deadlock commit.

Revoke descriptor credits are charged based on `j_revoke_records_per_block`.

## Barriers and Update Quiescing

`jbd2_journal_lock_updates()` blocks new normal updates, waits for reserved credits and active transaction updates to drain, and then serializes special journal-locked operations through `j_barrier`.

`jbd2_journal_unlock_updates()` drops the barrier and wakes blocked starters. Reserved handles are allowed through some barriers to avoid writeback deadlocks.

## Metadata Access Paths

`jbd2_journal_get_write_access()` gives a handle permission to modify an existing metadata buffer. It checks filesystem device writeback errors, attaches a journal head, handles dirty non-JBD buffers, performs copy-out if the buffer belongs to the committing transaction, and cancels any revoke.

`jbd2_journal_get_create_access()` handles newly created locked buffers, allowing only safe states: no transaction, current transaction, or committing transaction on `BJ_Forget`.

`jbd2_journal_get_undo_access()` preserves committed data for non-rewindable operations such as bitmap updates, storing `b_committed_data` after write access succeeds.

`jbd2_write_access_granted()` is a lockless fast path that verifies a buffer is already attached to the handle’s transaction, using RCU and barriers to avoid stale `journal_head` reuse.

## Dirtying and Forgetting Buffers

`jbd2_journal_dirty_metadata()` marks a previously accessed buffer as modified, consumes one metadata credit once per transaction, sets `buffer_jbddirty`, and files it on the transaction metadata list unless it is still owned by the committing transaction.

`jbd2_journal_forget()` removes a buffer from journaling interest, handling current-transaction buffers, committing-transaction buffers, checkpointed buffers, freed buffers, and dirty/writeback cases. It may refile buffers on `BJ_Forget` so checkpoint cleanup remains ordered with the transaction deleting the block.

## Buffer List Management

The file implements transaction buffer circular lists and list transitions:
- `__blist_add_buffer()`
- `__blist_del_buffer()`
- `__jbd2_journal_temp_unlink_buffer()`
- `__jbd2_journal_unfile_buffer()`
- `__jbd2_journal_file_buffer()`
- `jbd2_journal_file_buffer()`
- `__jbd2_journal_refile_buffer()`
- `jbd2_journal_refile_buffer()`

List types include metadata, forget, shadow, and reserved buffers. Dirty state is hidden from the VM as `buffer_jbddirty` while JBD2 controls writeout.

## Folio Invalidation and Buffer Freeing

`jbd2_journal_try_to_free_buffers()` removes clean checkpoint references from a locked folio and then delegates to `try_to_free_buffers()` if no JBD buffers remain.

`jbd2_journal_invalidate_folio()` and `journal_unmap_buffer()` handle truncation invalidation. They carefully distinguish buffers with no transaction, checkpointed buffers, committing transaction buffers, and running transaction buffers. Partial-page invalidation can return `-EBUSY` if a buffer is in the committing transaction and cannot be safely discarded yet.

## Ordered Data Inode Tracking

`jbd2_journal_inode_ranged_write()` and `jbd2_journal_inode_ranged_wait()` attach `jbd2_inode` objects to the transaction inode list and track dirty page ranges. `jbd2_journal_begin_ordered_truncate()` starts writeout of truncated data when that inode’s data belongs to the committing transaction.

## Important Invariants

- A handle must not cross journals; nested starts on the same journal only bump `h_ref`.
- `t_updates` pins a transaction against commit state changes while handles are active.
- Buffers belonging to the committing transaction require frozen copy-out before current transaction modification.
- Dirty metadata buffers should be tracked as `buffer_jbddirty`, not normal `buffer_dirty`, while journal-owned.
- `b_next_transaction` represents handoff from committing to running transaction.
- Truncate invalidation relies on filesystem ordering: on-disk inode size/orphan state must be updated before data buffers are discarded.

## Research Notes

This is the highest-risk JBD2 state-machine file in the group. It encodes subtle crash-consistency and deadlock-avoidance rules around credit reservation, committing transaction copy-out, checkpoint pinning, buffer reuse after free, and ordered-data truncation.
