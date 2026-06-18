# sources/storage-engines/wiredtiger/test/suite/test_txn23.py

## Purpose
`test_txn23.py` ensures read timestamps are not cleared or lost under cache pressure while multiple historical versions exist.

## Important APIs, Types, and Functions
The class defines `large_updates`, `check`, and `test_txn`. It uses `SimpleDataSet`, timestamped commit transactions, `conn.set_timestamp`, read timestamp transactions, and a small 5 MB cache.

## Control Flow
Two tables are created. Oldest and stable are pinned at 10. Four rounds of large updates write 2,000 rows per table at timestamps 20, 30, 40, and 50. The test then reads every row at each timestamp and expects the corresponding value.

## State and Persistence Behavior
Each key has a timestamped update chain. Cache pressure from large values should not cause WiredTiger to clear the active read timestamp and return the wrong version.

## Dependencies and Integration Points
Depends on timestamp visibility, history-store/cache behavior, and `SimpleDataSet`.

## Risks and Edge Cases
Small cache plus many large updates stresses eviction. The test may be runtime-heavy because it performs many timestamped transactions and reads.

## Test Signals
Every read at timestamps 20, 30, 40, and 50 returns the value committed at that timestamp.
