# sources/storage-engines/wiredtiger/test/suite/test_layered_cursor13.py

Purpose: regression coverage for bounded layered cursors on a follower over a 1000-key dataset. It verifies lower and upper cursor bounds, inclusive and exclusive edge behavior, nonexistent bound keys, tombstones, search/search_near under bounds, bound rebinding, and positioned updates during scans.

Important APIs and types: `test_layered_cursor13` derives from `wttest.WiredTigerTestCase` and is wrapped by `@disagg_test_class`. It uses `gen_disagg_storages(..., disagg_only=True)` and `make_scenarios`, WiredTiger cursor APIs `bound`, `next`, `prev`, `search`, `search_near`, `update`, `set_key`, `set_value`, and transaction timestamps through `timestamp_str`. Helpers include `insert_stable`, `insert_ingest`, `remove_ingest`, `populate_*`, `set_bounds`, `scan_forward`, `scan_backward`, `open_bounded_cursor`, and `expected_range`.

Control flow: `setUp` creates the same layered URI on leader and follower sessions. Stable rows are written on the leader, checkpointed, and exposed to the follower with `disagg_advance_checkpoint`; ingest rows and tombstones are written directly on the follower. Each test populates one data layout, opens a bounded follower cursor, scans or searches, then asserts returned key order and visibility.

State and persistence behavior: stable data represents checkpointed leader state, while ingest data and tombstones represent follower-local overlay state. The tests exercise merge ordering across stable and ingest constituents, and assert tombstones hide stable values even inside or at bounds. Timestamped commits and stable timestamp advancement make the checkpoint boundary explicit.

Dependencies and integration: integrates with WiredTiger disaggregated storage helpers, layered table creation, cursor bounds, and follower checkpoint advancement. Risks are off-by-one bound filtering, stale constituent cursor position after bound changes, tombstone leakage, and write positioning corrupting a scan. Test signals are direct equality checks for complete key ranges and explicit `WT_NOTFOUND`/search result assertions.
