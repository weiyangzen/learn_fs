# File Research: sources/os/linux/linux/fs/jbd2/checkpoint.c

Implements JBD2 checkpointing: writing committed metadata buffers to their home locations so journal log space can be reused.

Space management:
- `__jbd2_log_wait_for_space()` waits until enough journal space exists. It may run checkpointing, clean the journal tail, wait for committing transactions, or abort if no progress is possible.
- `jbd2_cleanup_journal_tail()` gets the oldest needed transaction/block, optionally flushes the filesystem device for barriers, and updates the journal tail unless the journal is aborted.

Checkpoint execution:
- `jbd2_log_do_checkpoint()` cleans the tail, selects the oldest checkpoint transaction, walks its checkpoint buffers, waits for buffers in other running transactions, queues dirty home-location writes in batches, removes clean buffers from checkpoints, yields as needed, and finally cleans the tail.
- `__flush_batch()` writes queued checkpoint buffers with a block plug and releases references.

Checkpoint list maintenance:
- `__jbd2_journal_insert_checkpoint()` links a dirty/jbddirty journal head onto a transaction checkpoint list and grabs a journal-head reference.
- `__jbd2_journal_remove_checkpoint()` unlinks a checkpointed buffer, drops the journal-head reference, updates counters, and if the transaction is finished and empty, drops/frees it.
- `jbd2_journal_try_remove_checkpoint()` removes only if the buffer is not part of a transaction, can be locked, and is clean.
- `__buffer_unlink()` handles circular checkpoint list unlinking.

Shrinker/destruction:
- `journal_shrink_one_cp_list()` and `jbd2_journal_shrink_checkpoint_list()` opportunistically remove written-back checkpoint buffers for memory reclaim.
- `__jbd2_journal_clean_checkpoint_list()` scans checkpoint transactions with selectable behavior for busy buffers.
- `jbd2_journal_destroy_checkpoint()` removes all checkpoint buffers during journal abort/destruction.
- `__jbd2_journal_drop_transaction()` unlinks a finished transaction from the checkpoint transaction ring and asserts all lists/references are clear.

The file is heavily lock-sensitive, using `j_state_lock`, `j_list_lock`, and `j_checkpoint_mutex` to coordinate committing, checkpointing, reclaim, and journal tail updates.
