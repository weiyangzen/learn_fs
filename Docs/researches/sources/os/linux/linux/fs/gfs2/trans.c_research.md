# File Research: sources/os/linux/linux/fs/gfs2/trans.c

## Scope

This file implements GFS2 transaction begin/end logic and helpers that attach metadata buffers, journaled data buffers, and revoke records to the active transaction. It mediates between filesystem mutation paths and the GFS2 log subsystem.

## Public And Internal APIs Covered

- Transaction lifecycle: `__gfs2_trans_begin()`, `gfs2_trans_begin()`, `gfs2_trans_end()`, `gfs2_trans_free()`.
- Buffer attachment: `gfs2_trans_add_data()`, `gfs2_trans_add_databufs()`, `gfs2_trans_add_meta()`.
- Revoke handling: `gfs2_trans_add_revoke()`, `gfs2_trans_remove_revoke()`.
- Diagnostics/allocation: `gfs2_print_trans()`, `gfs2_alloc_bufdata()`.

## Control Flow And Behavior

`__gfs2_trans_begin()` rejects nested transactions, zero-sized reservations, and withdrawn filesystems. It records the caller instruction pointer, block/revoke request, and reserved log block estimate. Metadata/data log descriptor overhead is included in `tr_reserved`. The function starts an internal write, takes `sd_log_flush_lock` for reading, verifies `SDF_JOURNAL_LIVE`, tries fast log/revoke reservation, and falls back to full reservation outside the lock if needed. Extra revokes are returned to the pool once the reservation is established.

`gfs2_trans_begin()` allocates a transaction object from `gfs2_trans_cachep` and delegates to `__gfs2_trans_begin()`. `gfs2_trans_end()` clears `current->journal_info`, releases all revokes and log blocks if the transaction was untouched, otherwise releases unused revokes, verifies that attached buffers/revokes fit reservations, commits the transaction to the log, frees unattached heap transactions, releases the log flush read lock, optionally flushes synchronously mounted filesystems, and ends the internal write.

`gfs2_trans_add_data()` attaches data buffers for journaled data mode. It handles already pinned buffers, allocates `gfs2_bufdata` if needed under `sd_log_lock`, asserts glock ownership, marks the glock dirty/LFLUSH, pins the buffer, increments data-buffer counts, and links it onto `tr_databuf`.

`gfs2_trans_add_meta()` follows similar mechanics for metadata, but validates the metadata magic before journaling, rejects adding buffers after withdrawal or complete freeze, pins the buffer, zeroes pad state, stamps the journal id into the metadata header, increments metadata-buffer counts, and links onto `tr_buf`.

`gfs2_trans_add_databufs()` walks folio buffer heads intersecting a byte range, marks them uptodate, and calls `gfs2_trans_add_data()`. Revoke removal scans `sd_log_revokes` for block numbers in the newly allocated range, removes matching revoke records, updates counters, detaches glock revoke state, frees bufdata, and releases revoke reservations.

## State And Data Structures

Transactions track requested blocks/revokes, actual new/removed metadata/data buffers, revoke count, flags such as `TR_TOUCHED`, `TR_ONSTACK`, and `TR_ATTACHED`, and per-transaction lists for data, metadata, and AIL state. Buffer heads use `b_private` for `struct gfs2_bufdata`.

## Dependencies

The file depends on GFS2 log reservation/commit/revoke APIs, glock dirty state, metadata headers, buffer head locking/pinning, folio buffers, superblock freeze state, and the VFS internal write accounting.

## Risks And Invariants

Only one transaction may exist per task through `current->journal_info`. Every mutating path must reserve enough blocks and revokes before calling add functions. Metadata buffers must have valid GFS2 magic before journaling. The log flush lock prevents inconsistent revoke accounting during flush. Adding metadata after `SB_FREEZE_COMPLETE` causes withdrawal because it violates freeze guarantees.
