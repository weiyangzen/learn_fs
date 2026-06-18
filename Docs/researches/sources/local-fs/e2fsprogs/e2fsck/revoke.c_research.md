# File Research: sources/local-fs/e2fsprogs/e2fsck/revoke.c

This file implements JBD2 revoke handling for commit-time journal records and recovery-time replay suppression.

Purpose:
- A revoke record prevents an old journaled metadata block from being replayed over newer data after a block has been freed and reused.
- Revoke semantics handle ordering: later journal data can override earlier revoke, while later revoke suppresses earlier journal data.

Data structures:
- `struct jbd2_revoke_record_s` records a revoked block and transaction sequence.
- `struct jbd2_revoke_table_s` is a power-of-two hash table of revoke records.
- Two revoke tables alternate between running and committing transactions.

Cache/table lifecycle:
- `jbd2_journal_init_revoke_record_cache()` and `jbd2_journal_init_revoke_table_cache()` create slab caches in kernel builds.
- Destroy helpers tear them down.
- `jbd2_journal_init_revoke()` allocates two hash tables and initializes locking.
- `jbd2_journal_destroy_revoke()` destroys empty tables.

Commit-time revoke path, kernel-only:
- `jbd2_journal_revoke(handle, blocknr, bh_in)` sets the journal revoke feature, marks matching buffers revoked/revoke-valid, calls `jbd2_journal_forget()` when needed, consumes revoke credits, and inserts a revoke record for the running transaction.
- `jbd2_journal_cancel_revoke(handle, jh)` cancels a pending revoke when a buffer gets journal write access.
- `jbd2_clear_buffer_revoked_flags()` clears buffer flags at transaction boundaries.
- `jbd2_journal_switch_revoke_table()` swaps running and committing revoke tables.
- `jbd2_journal_write_revoke_records()` writes all committing revoke records into journal revoke descriptor blocks.
- `write_one_revoke_record()` and `flush_descriptor()` format revoke blocks, including 64-bit block numbers and descriptor checksums.

Recovery revoke path:
- `jbd2_journal_set_revoke(journal, blocknr, sequence)` records the latest revoke transaction for a block.
- `jbd2_journal_test_revoke(journal, blocknr, sequence)` decides whether a log block should be skipped during replay.
- `jbd2_journal_clear_revoke(journal)` empties the table after recovery.

Integration points:
- Used by `recovery.c` during revoke scan and replay.
- Uses JBD2 transaction, buffer-head, list, spinlock, slab, hash, and checksum infrastructure.
- Userland e2fsprogs builds share the recovery-facing code through `jfs_user.h`.

Risk notes:
- The running revoke table is protected by `j_revoke_lock`; committing and recovery tables rely on single-threaded access by design.
- `handle->h_revoke_credits` exhaustion is treated as IO failure.
- Multiple revoke records for the same block retain only the newest transaction sequence.
