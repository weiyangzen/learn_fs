# sources/storage-engines/wiredtiger/test/suite/test_prepare_discover09.py

Purpose: verifies a single prepared transaction spanning both a layered table and a non-layered local table is surfaced once by follower `prepared_discover:` and resolved consistently for all participating tables.

Important APIs and types: `@skip_for_hook("tiered")`, `@disagg_test_class`, `local_uri`, `layered_uri`, helper methods `populate_and_prepare`, `reopen_as_follower`, `discover_and_resolve`, `assert_table_state`, `claim_prepared_id`, and commit/rollback scenarios.

Control flow: both tables are created and receive committed keys 1-3 at timestamp 60. One transaction writes prepared keys 4-6 to both tables with prepared id `0x1234`, stable advances, and the leader checkpoints. After reopening as follower, the discover cursor claims and commits or rolls back the id, then each table is read at timestamp 250.

State and persistence behavior: prepared metadata must represent a cross-table transaction as one prepared id. Resolution must atomically affect all written btrees, not just the layered table.

Dependencies and integration points: disaggregated checkpoint transfer, local non-logged table handling, layered table ingest, timestamp visibility, and prepared transaction coordinator metadata.

Risks: cross-table resolution is a broad integration surface; partial application would leave divergent local/layered state. Tiered storage is skipped because layered tables are unsupported there.

Test signals: discovered ids equal `[0x1234]`; committed keys are always visible; prepared keys are visible after commit resolution and `WT_NOTFOUND` after rollback resolution on both URIs.
