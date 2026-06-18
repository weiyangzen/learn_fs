# sources/storage-engines/wiredtiger/test/suite/test_timestamp01.py

## Purpose
`test_timestamp01.py` covers basic timestamp parsing and range validation for transaction commit timestamps.

## Important APIs, Types, and Functions
The class `test_timestamp01` inherits `WiredTigerTestCase` and `suite_subprocess`. The single method `test_timestamp_range` uses `session.begin_transaction`, `session.timestamp_transaction`, `session.commit_transaction`, `timestamp_str`, and `assertRaisesWithMessage`.

## Control Flow
The test first asserts that setting a commit timestamp outside a running transaction fails. It then starts separate transactions to validate rejection of zero timestamps, overly long hexadecimal timestamps, negative timestamp formatting, and invalid non-hex characters. Finally it commits transactions with valid timestamp forms: timestamp one, uppercase hex, and the maximum 64-bit timestamp expression used by the test.

## State and Persistence Behavior
No table is created and no records are written. The state under test is transaction timestamp metadata attached to running transaction handles and parser acceptance/rejection.

## Dependencies and Integration Points
It integrates with WiredTiger transaction timestamp parsing, Python binding error reporting, `timestamp_str`, and subprocess-capable test harness behavior.

## Risks and Test Signals
Risks include accepting invalid timestamps, rejecting valid uppercase hex, or allowing timestamp assignment without an active transaction. Signals are expected errors and successful commits for valid boundary inputs.
