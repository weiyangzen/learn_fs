# sources/storage-engines/wiredtiger/test/suite/test_timestamp05.py

## Purpose
`test_timestamp05.py` checks that timestamped create and bulk-load workflows can checkpoint at a stable timestamp without leaking timestamps into metadata or failing dirty-tree handling.

## Important APIs, Types, and Functions
The class uses `WiredTigerTestCase`, `suite_subprocess`, `make_scenarios`, and two tests: `test_create` and `test_bulk`. Scenarios vary integer-row and column-store key formats.

## Control Flow
`test_create` sets oldest/stable to 50, creates a table inside a transaction committed at timestamp 100, writes an additional value to dirty the tree, and checkpoints with `use_timestamp=true`. `test_bulk` creates a table, bulk-loads 100 records through a bulk cursor, sets timestamps to 50, closes the bulk cursor in a transaction committed at timestamp 100, dirties the tree, and checkpoints at stable timestamp. The bulk test is skipped for the disaggregated hook.

## State and Persistence Behavior
The test focuses on metadata and checkpoint interactions rather than explicit readback. It exercises timestamped schema creation and bulk completion when the stable checkpoint timestamp precedes the create/bulk commit timestamp.

## Dependencies and Integration Points
It integrates with session create, bulk cursor close, transaction commit timestamps, stable timestamp checkpoints, and hook-specific bulk support.

## Risks and Test Signals
The risk is incorrectly timestamping metadata or mishandling dirty pages whose create/bulk timestamp is newer than stable. The signal is completing both workflows without errors.
