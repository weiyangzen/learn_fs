# sources/storage-engines/wiredtiger/test/suite/test_layered_config10.py

Purpose: tests `disaggregated=(storage_tier=cold)` table configuration validation and cold-tier read/write statistics.

Important APIs/types/functions: uses `DisaggConfigMixin`, `validate_config`, `reopen_conn`, metadata cursor reads, stats `stat.conn.disagg_block_put_cold` and `stat.conn.disagg_block_get_cold`, `verifyUntilSuccess`, and leader role reconfiguration.

Control flow: `test_disagg_storage_tier` tries invalid empty storage tier, no storage tier, valid `cold`, and invalid typo `coldd`, asserting metadata string presence/absence and invalid-argument errors. `test_cold_write` creates a cold table, checks cold put stat zero, writes/checkpoints 1,000 rows, and asserts cold puts increased. `test_cold_read` creates and checkpoints a cold table, asserts cold gets zero, verifies the table to force page reads, and asserts cold gets increased.

State and persistence behavior: table metadata persists optional `storage_tier=cold` only when configured. Cold tier stats prove disaggregated block operations are routed to cold storage for checkpointed pages and verify reads.

Dependencies/integration points: table config parser, metadata persistence, disaggregated block manager, cold tier stats, and verify.

Risks: stat assertions assume no earlier cold operations in the connection. Error checks rely on stderr pattern `Invalid argument`.

Test signals: pass means storage-tier config is validated/persisted and cold-tier read/write accounting is exercised.
