# sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint13.py

Purpose: tests the materialization frontier behavior in disaggregated storage, ensuring data remains readable when the last materialized LSN is set behind the newest checkpoint LSN.

Important APIs/types/functions: uses `conn.get_page_log`, page-log APIs `pl_get_last_lsn`, `pl_set_last_materialized_lsn`, connection `reconfigure(disaggregated=(last_materialized_lsn=...))`, debug cursor config `debug=(release_evict)`, and a shared-table scenario using `block_manager=disagg,log=(enabled=false)`.

Control flow: the test sets stable timestamp 1, obtains the page log, steps up to leader, creates a shared disaggregated table, writes value `b`, checkpoints, records checkpoint 1 LSN, writes value `c`, checkpoints, and records checkpoint 2 LSN. It sets the materialized LSN back to checkpoint 1, reconfigures the connection with that frontier, forces eviction through a debug cursor, then rereads the row expecting the latest value `c`.

State and persistence behavior: persistent state includes page-log records, checkpoint LSNs, and last-materialized LSN. The test confirms that materialization frontier configuration does not make the latest checkpoint data unreadable after eviction.

Dependencies/integration points: direct page-log extension, disaggregated block manager, eviction/reconciliation, and materialization frontier reconfiguration.

Risks: single-key coverage narrows page-shape diversity. It relies on debug eviction successfully forcing a reload path.

Test signals: pass indicates eviction/read can navigate page-log materialization state and return the newest checkpointed value.
