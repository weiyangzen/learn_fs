# File Research: sources/os/linux/linux-stable/fs/jbd2/transaction.c

## Scope
Implements JBD2 transaction and handle management: transaction creation, handle start/stop/restart, credit accounting, reserved handles, update barriers, write/create/undo access, metadata dirtying, forget/invalidate/free-buffer paths, transaction buffer-list management, and ordered-data inode tracking.

## Primary APIs
Key APIs include `jbd2__journal_start()`, `jbd2_journal_start()`, `jbd2_journal_start_reserved()`, `jbd2_journal_free_reserved()`, `jbd2_journal_extend()`, `jbd2__journal_restart()`, `jbd2_journal_restart()`, `jbd2_journal_stop()`, `jbd2_journal_lock_updates()`, `jbd2_journal_unlock_updates()`, write/create/undo access functions, `jbd2_journal_dirty_metadata()`, `jbd2_journal_forget()`, `jbd2_journal_try_to_free_buffers()`, `jbd2_journal_invalidate_folio()`, buffer filing/refiling helpers, and ordered inode range helpers.

## Behavior
Starting a handle attaches it to the running transaction or creates a new one. Credit accounting enforces per-transaction limits, reserved-credit limits, revoke descriptor space, and log-space availability before metadata is dirtied. Handles enter `memalloc_nofs` context to avoid filesystem recursion.

Reserved handles can join locked transactions without waiting for commits, supporting writeback paths that must not deadlock. Update barriers block new normal handles, wait for reserved credits and active updates to drain, then serialize special operations with `j_barrier`.

Write access attaches buffers to `BJ_Reserved`, handles copy-out when an older committing transaction owns the buffer, waits on shadow buffers, preserves frozen/committed copies for undo access, and cancels revokes. Dirty metadata moves buffers to `BJ_Metadata` and consumes credits once per modified buffer.

Forget/invalidate paths handle buffers in current, committing, checkpointed, or no transaction state. They preserve checkpoint dependencies with `BJ_Forget`, mark committing buffers freed, and avoid unsafe truncation of partial-page buffers belonging to the committing transaction.

Stopping a handle returns unused credits, accounts revoke descriptor credits actually needed, optionally batches synchronous commits, requests commits for sync or expired transactions, and waits for sync commit completion.

## State And Data
Transactions track state, TID, start/expiry times, update count, outstanding credits/revokes, buffer lists (`BJ_Metadata`, `BJ_Reserved`, `BJ_Shadow`, `BJ_Forget`), inode list, and commit statistics. Journal heads track current/next/checkpoint transactions, list type, frozen data, committed data, triggers, modified state, and buffer linkage.

## Dependencies
Integrates with `journal.c` commit scheduling, `commit.c` transaction commit, `checkpoint.c`, revoke cancellation, buffer-head/page-cache APIs, folio invalidation, VFS writeback, tracepoints, and filesystem ordered-data users such as ext4.

## Risks And Invariants
Credit accounting is central: dirtying without credits corrupts transaction bounds. Copy-out must protect committing transaction contents while allowing new writes. `b_transaction`/`b_next_transaction` transitions require correct lock ordering. Truncate invalidation depends on filesystem orphan/i_size ordering to avoid replaying stale data.
