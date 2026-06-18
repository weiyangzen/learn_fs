# sources/storage-engines/wiredtiger/test/suite/test_txn28.py

## Purpose
`test_txn28.py` checks that `conn.debug_info('txn')` reports snapshot arrays whose printed count matches the number of IDs shown.

## Important APIs, Types, and Functions
The class defines regex helpers `get_number_after_substring`, `count_integers_between_substrings`, and `test_snapshot_array_dump`. It uses `expectedStdoutPattern`, `conn.debug_info('txn')`, and reads `stdout.txt`.

## Control Flow
The test creates a table, opens three sessions with active transactions and updates, dumps transaction debug info, scans stdout lines containing `snapshot count`, counts integer IDs inside the `snapshot: [...]` segment, and compares the two counts. It also tracks the maximum count.

## State and Persistence Behavior
State is in-memory transaction snapshot arrays for concurrent transactions. The filesystem is used only to read captured stdout.

## Dependencies and Integration Points
Depends on debug-info formatting, stdout capture naming, regex parsing, and transaction snapshot internals.

## Risks and Edge Cases
The file appears to open `cursor3` from `session2` while beginning `session3`, which may reduce intended coverage or rely on shared transaction state. Formatting changes can break parsing.

## Test Signals
Every printed snapshot count equals the number of integers in its snapshot list, and the maximum list length is 2.
