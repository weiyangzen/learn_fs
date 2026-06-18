# File Research: sources/os/linux/linux/fs/jbd2/revoke.c

## Role

`revoke.c` implements JBD2 revoke records. Revokes prevent old journal records for deleted or reallocated metadata blocks from being replayed after a crash and overwriting newer contents at the same filesystem block number.

## Data Structures

- `struct jbd2_revoke_record_s`: one revoked block and its transaction sequence, stored in a hash chain.
- `struct jbd2_revoke_table_s`: hash table of revoke records with power-of-two sizing.
- `journal->j_revoke_table[2]`: double-buffered tables for running and committing transactions.
- `journal->j_revoke`: points to the current running transaction’s revoke table.

## Runtime Revoke Path

`jbd2_journal_revoke()`:
- Ensures the journal supports the revoke incompatible feature.
- Finds the target buffer if not supplied.
- Checks revoke credits.
- Marks the buffer `Revoked` and `RevokeValid` when present.
- Calls `jbd2_journal_forget()` for supplied journaled buffers.
- Inserts a revoke record for the current transaction.

`jbd2_journal_cancel_revoke()` is called when a block is journaled again in the same transaction. It clears cached revoke state and removes the hash record if needed. It also clears revoked state on hashed aliases for non-blockdev mappings.

## Commit-Time Revoke Writing

`jbd2_journal_switch_revoke_table()` swaps the running and committing revoke tables and reinitializes the new running table.

`jbd2_journal_write_revoke_records()` walks the committing revoke table, writes records into revoke descriptor blocks, deletes in-memory records, and flushes the final descriptor.

`write_one_revoke_record()` writes 32-bit or 64-bit block numbers depending on journal features and allocates new revoke descriptor buffers as needed. `flush_descriptor()` fills `r_count`, sets descriptor checksums, marks the descriptor for journal write, and submits it.

## Recovery Revoke Path

During replay:
- `jbd2_journal_set_revoke()` inserts or updates the latest transaction sequence for a revoked block.
- `jbd2_journal_test_revoke()` returns true when a replay candidate is covered by a revoke record from the same or later transaction.
- `jbd2_journal_clear_revoke()` frees all replay revoke records.

## Cache and Table Lifecycle

The file owns slab caches for revoke records and revoke table headers:
- `jbd2_journal_init_revoke_record_cache()`
- `jbd2_journal_init_revoke_table_cache()`
- `jbd2_journal_destroy_revoke_record_cache()`
- `jbd2_journal_destroy_revoke_table_cache()`

Per-journal tables are created by `jbd2_journal_init_revoke()` and destroyed by `jbd2_journal_destroy_revoke()`.

## Locking Model

The comments define the central lock model:
- The committing table is accessed only by `kjournald2`, so it needs no hash-list lock.
- The running table is accessed by holders of transaction handles and protected by `j_revoke_lock` for hash-chain modifications.
- Replay runs before the filesystem is mounted and needs no concurrent access protection.

## Important Invariants

- A block revoked then journaled in the same transaction must cancel the revoke.
- A block journaled then revoked in the same transaction must have the revoke take precedence; revoke records are written later than normal journal data.
- Data writes do not cancel revokes because old metadata replay must still be prevented.
- Revoke credits are mandatory; running out is treated as serious corruption/error.
- Destroying a revoke table asserts all hash chains are empty.

## Research Notes

The file is small but central to crash consistency. Its correctness depends on preserving the ordering relationship between journal data records and revoke descriptors, plus maintaining accurate cached revoke bits on buffer heads and aliases.
