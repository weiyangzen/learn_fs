# File Research: sources/os/linux/linux-stable/fs/jbd2/journal.c

## Scope
Implements core JBD2 journal object lifecycle, kjournald2 thread management, commit scheduling/waiting, log block allocation, journal superblock validation/update, feature negotiation, flush/wipe/abort handling, journal-head allocation, JBD inode lifecycle, proc stats, shrinker integration, and module cache initialization/destruction.

## Primary APIs
Exports journal control and lifecycle APIs including `jbd2_journal_init_dev()`, `jbd2_journal_init_inode()`, `jbd2_journal_load()`, `jbd2_journal_destroy()`, `jbd2_journal_flush()`, `jbd2_journal_wipe()`, `jbd2_journal_abort()`, `jbd2_journal_errno()`, `jbd2_journal_clear_err()`, `jbd2_journal_ack_err()`, `jbd2_log_wait_commit()`, `jbd2_journal_start_commit()`, `jbd2_journal_force_commit()`, `jbd2_complete_transaction()`, fast-commit buffer helpers, and journal-head helpers.

## Behavior
`kjournald2()` runs the journal thread, waking for explicit commit requests, commit timer expiry, freezer events, and unmount. It calls `jbd2_journal_commit_transaction()` outside `j_state_lock` and coordinates completion with `j_wait_done_commit`.

Commit control is transaction-id based. `__jbd2_log_start_commit()` requests commit of the running transaction, `jbd2_log_wait_commit()` sleeps until `j_commit_sequence` reaches a requested TID, and force/complete helpers start commits when needed before waiting.

Log allocation advances the circular log head with `jbd2_journal_next_log_block()`. Descriptor buffers are allocated and initialized with JBD2 magic, block type, and transaction sequence. Metadata write buffers handle magic-number escaping and shadow/frozen-data attachment.

Journal initialization loads and validates the on-disk superblock, checks block size, max length, feature flags, checksum versions, checksum type, and fast-commit area sizing. `journal_reset()` positions head/tail and starts kjournald2 after recovery.

Superblock writes use high-priority journal request flags, optional barriers/FUA, checksum refresh, synchronous buffer submission, and abort-on-write-error behavior. Flush checkpoints all committed transactions, cleans the tail, marks the journal empty, and can discard or zero journal blocks.

## State And Data
Key state includes `j_running_transaction`, `j_committing_transaction`, checkpoint lists, `j_head`, `j_tail`, `j_free`, transaction sequences, `j_flags`, superblock buffer, fast-commit bounds/buffers, revoke tables, waitqueues, shrinker counters, proc stats, and slab caches.

## Dependencies
Depends on block-device buffer I/O, transaction commit/checkpoint code, revoke setup, recovery replay, kernel shrinkers, procfs/seq_file, timers, kthreads, freezer support, slab/vmalloc allocation, and tracepoints.

## Risks And Invariants
Journal tail updates must reach stable storage before log space is reused. Feature bits and checksum fields must remain consistent for readonly and recovery paths. Journal abort is permanent for the mount and must record errno carefully, with `-ESHUTDOWN` precedence. Journal-head refcounting protects buffer attachment from VM release and RCU slab reuse hazards.
