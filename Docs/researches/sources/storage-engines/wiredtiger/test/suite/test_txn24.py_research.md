# sources/storage-engines/wiredtiger/test/suite/test_txn24.py

## Purpose
`test_txn24.py` validates transaction/eviction interaction: eviction threads must make progress under long-running transactions, and verbose logging should identify the session pinning the oldest transaction ID.

## Important APIs, Types, and Functions
The class defines `conn_config`, `get_stat`, `test_snapshot_isolation_and_eviction`, and `test_oldest_id_log`. It uses eviction thread config, verbose transaction output, `wiredtiger.stat.conn.capacity_bytes_evict`, multiple sessions, and `captureout`.

## Control Flow
The first test populates 480,000 rows, checkpoints, starts a long transaction, updates many rows through three other sessions, then asserts eviction wrote bytes before the long transaction commits. The second starts two long transactions, advances many transaction IDs in a third session, commits the oldest, checkpoints, and checks verbose output.

## State and Persistence Behavior
Persistent table updates and cache eviction are both exercised. Transaction ID pinning state drives eviction and verbose diagnostics.

## Dependencies and Integration Points
Depends on WiredTiger eviction threads, capacity stats, verbose transaction messages, and `rollbacks_allowed = 0`.

## Risks and Edge Cases
Large row counts and eviction timing can be sensitive. Output text matching can break on diagnostic wording changes.

## Test Signals
Evicted bytes increase, and output contains "oldest id ... pinned in session".
