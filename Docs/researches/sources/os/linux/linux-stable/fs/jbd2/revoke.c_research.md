# File Research: sources/os/linux/linux-stable/fs/jbd2/revoke.c

## Scope
Implements JBD2 revoke records, which prevent stale logged metadata blocks from being replayed after deletion/reallocation. Covers revoke hash table allocation, runtime revoke/cancel operations, commit-time revoke descriptor writing, and recovery-time revoke tests.

## Primary APIs
Exports or provides `jbd2_journal_init_revoke_record_cache()`, `jbd2_journal_init_revoke_table_cache()`, `jbd2_journal_init_revoke_table()`, `jbd2_journal_init_revoke()`, `jbd2_journal_destroy_revoke()`, `jbd2_journal_revoke()`, `jbd2_journal_cancel_revoke()`, `jbd2_clear_buffer_revoked_flags()`, `jbd2_journal_switch_revoke_table()`, `jbd2_journal_write_revoke_records()`, `jbd2_journal_set_revoke()`, `jbd2_journal_test_revoke()`, and `jbd2_journal_clear_revoke()`.

## Behavior
Runtime revoke inserts a block record into the running transaction’s revoke hash and marks matching buffer heads with `BH_Revoked`/`BH_RevokeValid`. If a buffer is passed, it also calls `jbd2_journal_forget()` to remove it from current journaling state.

Cancel revoke is called when a block is journaled again in the same transaction. It uses cached buffer revoke bits when valid, otherwise searches the hash table and removes the record. It also clears revoked state on a hashed alias if the current buffer is not the blockdev mapping buffer.

Commit-time code switches revoke tables so the committing transaction owns one table and the new running transaction owns the other. It writes revoke records into `JBD2_REVOKE_BLOCK` descriptors, using 32-bit or 64-bit block numbers, with optional descriptor checksums.

Recovery-time revoke insertion records the latest sequence for each block. Replay tests skip a logged block when its transaction sequence is not newer than the revoke sequence.

## State And Data
`jbd2_revoke_record_s` stores hash link, transaction sequence, and block number. `jbd2_revoke_table_s` stores power-of-two hash size, shift, and list heads. `journal->j_revoke` points to the active runtime or replay table.

## Dependencies
Depends on transaction handles, buffer-head revoke state bits, journal descriptor allocation, feature setting (`JBD2_FEATURE_INCOMPAT_REVOKE`), commit code log buffer lists, and recovery replay.

## Risks And Invariants
A revoke after a journaled write must take precedence during recovery. A journaled write after a revoke must cancel the revoke. Revoke credits are enforced per handle. The committing revoke table is single-threaded under kjournald2; the running table uses `j_revoke_lock`.
