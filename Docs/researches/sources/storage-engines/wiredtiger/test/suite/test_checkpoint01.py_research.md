# sources/storage-engines/wiredtiger/test/suite/test_checkpoint01.py

Purpose: comprehensive checkpoint API suite covering named checkpoint contents, dropping, cursor opens, in-use protection, update rejection, reserved names, and empty checkpoints.

Important APIs/types/functions: multiple `WiredTigerTestCase` classes, `SimpleDataSet`, `make_scenarios`, `session.checkpoint` with `name`, `drop`, `from=all`, checkpoint cursors, `verifyUntilSuccess`, and `wiredtiger.WT_NOTFOUND`.

Control flow: `test_checkpoint` builds a sequence of named checkpoints over overlapping key ranges and verifies each checkpoint's expected record map as checkpoints are dropped. `test_checkpoint_cursor` covers non-existent checkpoint opens, multiple open cursors, and drop/regenerate failures while a cursor is in use. `test_checkpoint_cursor_update` asserts checkpoint cursors reject `insert`, `remove`, and `update`. `test_checkpoint_last` verifies `WiredTigerCheckpoint` resolves to the latest checkpoint repeatedly. `test_checkpoint_illegal_name` validates reserved checkpoint names and grouping characters. `test_checkpoint_empty` verifies named/unnamed checkpoints over empty objects and latest-checkpoint behavior after later writes.

State/persistence behavior: exercises checkpoint metadata lifecycle and immutable checkpoint snapshots under file/table URIs and precise/fuzzy checkpoint modes.

Dependencies/integration: named checkpoints are skipped for disaggregated and tiered where unsupported. Uses stable timestamp setup for precise checkpoints.

Risks/test signals: failure modes include wrong checkpoint contents, allowing illegal names, allowing writes on checkpoint cursors, or dropping in-use checkpoints.
