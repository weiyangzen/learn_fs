# sources/storage-engines/sqlite/src/backup.c

## Purpose

`backup.c` implements the `sqlite3_backup_*` online backup API and the internal btree copy path used by VACUUM-like operations. It copies pages from a source database btree to a destination btree incrementally, keeps copied pages current while the source changes, and finalizes destination schema and file-size state when the copy completes.

## Important APIs, Types, And Functions

The central type is `struct sqlite3_backup`, which records source and destination database handles and `Db` slots, destination schema cookie, destination transaction state, next source page, result code, remaining/pagecount counters, pager attachment state, and linked-list membership on the source pager.

Public entry points are `sqlite3_backup_init()`, `sqlite3_backup_step()`, `sqlite3_backup_finish()`, `sqlite3_backup_remaining()`, and `sqlite3_backup_pagecount()`. Pager callbacks enter through `sqlite3BackupUpdate()` and `sqlite3BackupRestart()`. Internal helpers include `findDatabase()`, `setDestPgsz()`, `checkReadTransaction()`, `isFatalError()`, `backupOnePage()`, `backupTruncateFile()`, and `attachBackupObject()`. `sqlite3BtreeCopyFile()` wraps the same machinery for complete btree-to-btree copies when VACUUM support is compiled in.

## Control Flow

`sqlite3_backup_init()` validates distinct source and destination handles, locks both connection mutexes, resolves database names, opens TEMP if requested, rejects an active destination read transaction, initializes `iNext` to page 1, and increments the source btree backup count.

`sqlite3_backup_step()` locks the source connection, source btree, and destination connection. If no fatal error has occurred, it rejects source write transactions, opens a source read transaction if needed, sets destination page size before the first write, opens a destination write transaction, rejects incompatible WAL or memdb page-size combinations, reads the source page count, and copies up to `nPage` pages with `backupOnePage()`. On completion, it handles empty source databases, bumps the destination schema cookie, resets destination schemas, sets WAL version if needed, truncates or pads the destination image for differing page sizes, commits the destination transaction, and returns `SQLITE_DONE`. If not complete, it attaches the backup object to the source pager so later source changes can repair already copied pages.

`sqlite3_backup_finish()` removes the backup from the pager list, decrements backup count, rolls back any open destination btree transaction, reports final status on the destination handle, frees heap-backed backup handles, and leaves/possibly closes zombie connections.

## State And Persistence Behavior

Destination database pages are persisted through pager writes and btree commits. `backupOnePage()` writes source page bytes into destination page spans, invalidates btree page extra state, and patches the database-size field on page 1 during normal copy. The source remains readable through a read transaction while pages are copied. Once attached to the pager backup list, already-copied pages are updated in place by `backupUpdate()` if the source connection modifies them; external source changes call `sqlite3BackupRestart()` to reset `iNext` to 1.

`nRemaining` and `nPagecount` are updated by `backup_step()` and are explicitly not thread-safe to read concurrently. `p->rc` preserves fatal errors across calls while allowing retry on `SQLITE_BUSY` and `SQLITE_LOCKED`.

## Dependencies And Integration Points

This file is tightly coupled to btree and pager internals: page sizes, page counts, pending-byte pages, journal modes, memdb handling, transaction phases, schema cookies, pager backup linked lists, pager file controls, OS file truncate/write/sync, and shared-cache btree mutexes. It also integrates with API armor, TEMP database opening, connection error state, zombie close handling, and optional `SQLITE_OMIT_VACUUM`.

## Risks And Edge Cases

Important risks include deadlocks from incorrect mutex order, copying page 1 metadata incorrectly, pending-byte page handling, differing page-size truncation, WAL destination restrictions, source writes racing with incremental copy, and failure during the commit/truncate path. `sqlite3BtreeCopyFile()` uses a stack `sqlite3_backup` with `pDestDb == 0`, so API code has branches where ownership and locking differ from public backup handles. Destination use by another thread during backup is documented as unsafe even though source-side APIs take locks.

## Test Signals

Tests should cover incremental and all-at-once backups, backup retry after busy source write transactions, source updates to already copied pages, restart after external source modification, page-size mismatch behavior, WAL and memdb restrictions, empty databases, schema cookie changes, progress counters, finish status mapping from `SQLITE_DONE` to `SQLITE_OK`, TEMP source/destination names, OOM and IO errors, and VACUUM copy behavior.
