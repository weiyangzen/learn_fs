# sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint03.py

Purpose: regression coverage for follower-side ingest-table pruning during disaggregated checkpoint pickup. It targets WT-15158 prune timestamp initialization, WT-15192 table-local checkpoint order mismatch, and first-GC behavior when older checkpoints are pinned by cursors.

Important APIs/types/functions: `test_layered_checkpoint03` extends `wttest.WiredTigerTestCase` and is wrapped by `disagg_test_class`; storage scenarios come from `gen_disagg_storages` and `make_scenarios`. Helpers `setup`, `leader_put_data`, `checkpoint`, `create_follower`, and `follower_open_close_dummy_cursor` orchestrate leader writes, stable timestamp advancement, leader checkpoints, follower connections, and checkpoint pickup through `disagg_advance_checkpoint`.

Control flow: setup creates one or more `layered:` URIs with `block_manager=disagg`, populates them, opens a follower, checkpoints, and advances the follower. The first test pins checkpoint 1 with an open follower cursor, creates checkpoint 2, opens a second table to initialize prune timestamp, then creates checkpoint 3. The second test forces one table through many checkpoint orders before checkpointing a second table. The third delays ingest GC participation until a cursor is opened on a previous checkpoint.

State and persistence behavior: mutable state is leader/follower connection state, timestamp counter, stable timestamps, table contents, and open cursors that pin historical checkpoint visibility. Persistence is via shared disaggregated metadata and follower ingest/stable table metadata.

Dependencies/integration points: depends on WiredTiger transactions, checkpoint metadata ordering, `disagg_advance_checkpoint`, and the disaggregated storage helper framework. It integrates with follower checkpoint pickup and ingest garbage collection code.

Risks: failures are timing/state bugs rather than simple value mismatches; tests mostly assert no crash/error, so regressions may surface as assertion failures, checkpoint pickup failures, or hangs. Cursor lifetime and per-table checkpoint order assumptions are central risk points.

Test signals: successful completion across disagg scenarios signals prune timestamps can be initialized/updated while older checkpoints are in use and while metadata order differs by table.
