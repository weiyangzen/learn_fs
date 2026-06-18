# sources/storage-engines/sqlite/src/test_journal.c

## Purpose

`test_journal.c` implements the `jt` VFS wrapper, a rollback-journal verifier that asserts SQLite journals and syncs original database pages before modifying them.

## Important APIs, types, and functions

`jt_file` stores real handle, file name, flags, lock state, transaction page count/page size, writable-page `Bitvec`, original page checksums, sync count, journal max offset, and linked-list state. Public APIs are `jt_register()` and `jt_unregister()`. Key helpers are `locateDatabaseHandle()`, `decodeJournalHdr()`, `openTransaction()`, `readJournalFile()`, and `closeTransaction()`.

## Control flow

The wrapper tracks open database and journal files. A valid first journal header starts transaction tracking and snapshots page checksums/freelist leaves. Journal syncs or header finalization read journal records, verify saved page checksums, and mark pages writable. Database writes and truncates assert that affected pages were safe to modify.

## State and persistence behavior

It delegates all real I/O and keeps only in-memory verification metadata. Transaction metadata is discarded when the journal is zeroed, truncated to zero, deleted, or the file closes. It temporarily disables global I/O-error simulation while reading verification data.

## Dependencies and integration points

It depends on SQLite VFS internals, `Bitvec`, rollback journal format, `PENDING_BYTE`, test I/O error globals, and SQLite mutexes. It integrates with rollback-journal pager tests and is not compatible with `PRAGMA synchronous=off`.

## Risks and test signals

Failures are assertion aborts. The code assumes journal naming and format details. Signals are absence of assertions under valid rollback journaling and assertion failures for unsafe writes, malformed journals, wrong journaled page images, or unsafe truncation.
