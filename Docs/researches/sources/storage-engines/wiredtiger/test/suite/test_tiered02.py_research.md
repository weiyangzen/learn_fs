# sources/storage-engines/wiredtiger/test/suite/test_tiered02.py

## Purpose
`test_tiered02.py` validates basic tiered table behavior across checkpoints, `flush_tier`, open cursors, connection restarts, and both simple and complex dataset layouts.

## Important APIs, Types, and Functions
`test_tiered02` combines `WiredTigerTestCase` with `TieredConfigMixin`. Scenarios come from `gen_tiered_storage_sources(..., tiered_only=True)` and a simple/complex dataset dimension. `get_dataset` selects `SimpleDataSet` or `ComplexDataSet`, `confirm_flush` checks the directory-store bucket object count, and `conn_extensions` loads the configured storage source extension.

## Control Flow
The test creates and populates a table with 10 rows, checkpoints, flushes to the shared tier, and verifies data. It closes and reopens the connection, grows the dataset to 50 rows while holding a table cursor open, checkpoints and flushes again, then grows to 100 and 200 rows with further checkpoints, flushes, cursor closure, and restart. Finally it appends 300 rows without a tier flush and checks that object count does not increase on plain checkpoint.

## State and Persistence Behavior
It exercises local object creation, shared-tier object copies, metadata survival across `close_conn`/`reopen_conn`, and readback from tiered objects after local state changes. Directory-store checks track monotonically increasing bucket entries only after flushes.

## Dependencies and Integration Points
The test integrates with `helper_tiered`, `wtdataset`, `os.listdir`, WiredTiger checkpoint configuration, and storage-source extension scenarios.

## Risks and Test Signals
It is sensitive to asynchronous object visibility, so `confirm_flush` retries before failing. Signals include dataset `check()` success after each phase and object-count increase only when `flush_tier` is expected.
