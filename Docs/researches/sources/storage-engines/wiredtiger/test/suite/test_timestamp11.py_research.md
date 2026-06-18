# sources/storage-engines/wiredtiger/test/suite/test_timestamp11.py

## Purpose
`test_timestamp11.py` verifies behavior when timestamped and non-timestamped transactions modify the same keys, especially across rollback-to-stable.

## Important APIs, Types, and Functions
The class uses `suite_subprocess`, `make_scenarios`, `session.begin_transaction('no_timestamp=true')`, `timestamp_transaction`, `conn.set_timestamp`, `session.checkpoint`, and `conn.rollback_to_stable`. Scenarios cover string-row and column-store keys.

## Control Flow
The test creates a file, inserts two keys at timestamp 2, updates one key at timestamp 5, then updates the other with `no_timestamp=true`. After setting stable to 2, checkpointing, and rolling back to stable, it verifies the timestamp 5 update rolled back while the no-timestamp update remains visible both with and without a read timestamp. It then repeats with the roles swapped, writes a timestamped value to the second key and a no-timestamp value to the first, and verifies reads without timestamp, at timestamp 2, and at timestamp 5.

## State and Persistence Behavior
Non-timestamped updates override timestamp visibility and survive rollback-to-stable. Timestamped updates newer than stable are rolled back unless reintroduced after rollback.

## Dependencies and Integration Points
It integrates MVCC timestamp visibility, no-timestamp transactions, checkpointing, rollback-to-stable, and row/column key formats.

## Risks and Test Signals
Risks include rolling back no-timestamp updates or hiding them at timestamped reads. Signals are exact value comparisons for both keys after rollback and at two read timestamps.
