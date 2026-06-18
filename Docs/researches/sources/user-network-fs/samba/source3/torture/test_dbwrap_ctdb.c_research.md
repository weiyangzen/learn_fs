# sources/user-network-fs/samba/source3/torture/test_dbwrap_ctdb.c

Purpose: This file tests basic transaction semantics for the CTDB-backed dbwrap backend. It verifies that a CTDB database can start/cancel transactions, store and overwrite integer records inside a transaction, commit, and read the committed values back.

Important APIs/types/functions: The only public entrypoint is `run_local_dbwrap_ctdb1()`. It uses `global_messaging_context()`, `db_open_ctdb()`, `dbwrap_transaction_start()`, `dbwrap_transaction_cancel()`, `dbwrap_transaction_commit()`, `dbwrap_store_uint32_bystring()`, and `dbwrap_fetch_uint32_bystring()`. The database is opened as `torture.tdb` with `DBWRAP_LOCK_ORDER_1`.

Control flow: The test opens a CTDB dbwrap context, starts and cancels an empty transaction, starts a second transaction, stores `"foo"=1`, `"bar"=5`, overwrites `"foo"=2`, verifies values before commit, commits, and verifies values after commit. Any unexpected NTSTATUS or nonzero transaction return jumps to cleanup.

State/persistence behavior: The test writes persistent records to the CTDB-backed TDB named `torture.tdb`. It intentionally validates that transaction commit reaches disk/backend state by fetching after commit. It does not unlink the database, so test isolation relies on deterministic overwrites of the specific keys.

Dependencies and integration points: It depends on dbwrap CTDB support, source3 messaging, CTDB message glue, global contexts, and the TDB/dbwrap API. It is a local torture test for database backend integration rather than SMB protocol behavior.

Risks: Requires CTDB dbwrap support and a functioning messaging context. Existing `torture.tdb` content for unrelated keys is ignored, but backend permission or cluster configuration can make open fail. Transaction bugs may appear as stale reads, lost overwrites, or commit failures.

Test signals: Expected key values are `"foo"=2` and `"bar"=5` both before and after commit. Failure messages identify transaction start/cancel/commit failures, store/fetch NTSTATUS, and mismatched fetched integer values.
