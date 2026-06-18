# sources/user-network-fs/samba/source3/lib/dbwrap/dbwrap_ctdb.c

Purpose: implements the dbwrap backend that exposes CTDB-clustered TDB databases through Samba's `db_context` API.

Important APIs/types/functions: `struct db_ctdb_ctx`, `struct db_ctdb_transaction_handle`, `struct db_ctdb_rec`, global `ctdb_async_ctx`, public `db_open_ctdb()` and `ctdb_async_ctx_reinit()`, plus transaction, fetch-lock, parse, async parse, traverse, delete, store, seqnum, and ID callbacks installed into `db_context`.

Control flow: open attaches to CTDB, resolves the local database path/open flags, optionally enables seqnums/read-only optimization, initializes async CTDB for non-persistent DBs, opens the local TDB copy, and configures callback methods. Non-persistent `fetch_locked` chainlocks the local TDB, checks whether the local header is writable dmaster state, migrates through CTDB if needed, then returns a locked record whose destructor unlocks and logs slow locks. Persistent DBs auto-start transactions: a global CTDB lock protects a marshalled write buffer, commit bumps an internal sequence-number record and sends `TRANS3_COMMIT`, retrying or accepting recovery-completed commits based on sequence comparison.

State and persistence: persistent local TDB copies contain CTDB ltdb headers plus payloads. Transactions store pending writes in `ctdb_marshall_buffer`; non-persistent deletes write tombstone-like empty records and schedule CTDB deletion. Async connection is process-global.

Dependencies/integration: CTDB daemon controls, `messaging_ctdb_connection()`, g_lock, dbwrap private API, TDB/tdb_wrap, loadparm thresholds, tevent async NTSTATUS, root elevation for async connection init.

Risks/test signals: transaction lock waits up to a day; nested cancel poisons later commit; empty records are treated as not found for non-persistent reads; commit recovery logic depends on sequence-number correctness. Tests should cover local read-only shortcuts, migration retry/log thresholds, locked-record destructor unlocks, persistent nested transactions, commit failure during recovery, transaction-buffer newest-value parsing, delete scheduling, traverse skipping `CTDB_DB_SEQNUM_KEY`, async parse request states, and open failures for missing CTDB/socket/dbpath.
