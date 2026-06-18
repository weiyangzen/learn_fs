# sources/storage-engines/wiredtiger/test/suite/test_timestamp13.py

## Purpose
`test_timestamp13.py` validates `session.query_timestamp` for commit, first-commit, prepare, and read timestamps.

## Important APIs, Types, and Functions
The class uses `suite_subprocess`, row/column scenarios, `session.query_timestamp`, `session.timestamp_transaction`, `session.prepare_transaction`, and `conn.set_timestamp`.

## Control Flow
`test_degenerate_timestamps` verifies all query choices return zero outside a transaction and before timestamps are set, and that an unknown query key is rejected. `test_query_read_commit_timestamps` sets a read timestamp, checks it, sets a commit timestamp and verifies both commit and first_commit, then sets a second commit timestamp and verifies only commit changes. `test_query_round_read_timestamp` starts a transaction with read timestamp rounding, sets a read timestamp below oldest, verifies it rounded to oldest, and confirms later oldest changes do not alter the stored read timestamp. `test_query_prepare_timestamp` prepares at timestamp 10, then sets commit/durable timestamp 20 and verifies prepare and commit queries.

## State and Persistence Behavior
The test inspects per-session transaction timestamp state. It does not depend on persisted records beyond table creation.

## Dependencies and Integration Points
It integrates with transaction timestamp bookkeeping, read timestamp rounding, prepare transaction state, and query validation.

## Risks and Test Signals
Risks include losing first-commit timestamp, reporting dynamic oldest instead of transaction read timestamp, or allowing invalid query keys. Signals are exact query timestamp values and expected error handling.
