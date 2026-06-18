# File Research: sources/os/linux/linux-stable/fs/jbd2/checkpoint.c

Implements JBD2 checkpointing: writing committed metadata from filesystem locations so journal log space can be reused.

Key paths:
- `__jbd2_log_wait_for_space()` waits until enough journal space exists, checkpointing old transactions, cleaning the tail, or waiting for committing transactions as needed. It aborts on impossible progress.
- `jbd2_log_do_checkpoint()` writes dirty checkpoint buffers from the oldest checkpoint transaction in batches, waits on busy buffers, starts/waits for newer transactions if a buffer is still attached, and cleans the journal tail afterward.
- `jbd2_cleanup_journal_tail()` finds the oldest remaining transaction, optionally flushes the filesystem device, and updates the journal tail.
- `jbd2_journal_shrink_checkpoint_list()` and `__jbd2_journal_clean_checkpoint_list()` free written-back checkpoint buffers under memory pressure or cleanup.
- `jbd2_journal_destroy_checkpoint()` removes all checkpoint state after abort/destroy.
- `__jbd2_journal_remove_checkpoint()` unlinks a buffer from a transaction checkpoint list and drops the transaction if it is finished and empty.
- `jbd2_journal_try_remove_checkpoint()` removes only clean, unlocked, non-transaction buffers.
- `__jbd2_journal_insert_checkpoint()` adds committed dirty buffers to a transaction checkpoint list.
- `__jbd2_journal_drop_transaction()` unlinks a finished transaction from checkpoint tracking and asserts it has no live lists.

Important locking:
- `j_state_lock` protects journal state and space decisions.
- `j_checkpoint_mutex` serializes checkpoint work and is temporarily dropped before waiting for commits that may need it.
- `j_list_lock` protects checkpoint transaction and journal_head lists.
- Buffer locks are used to determine whether checkpointed buffers are clean and stable.

Important invariants:
- Journal tail must not advance past metadata that failed checkpoint writeback.
- Checkpointing can proceed in abort state, but tail updates do not.
- Transactions are only dropped after `T_FINISHED` and empty checkpoint lists.
