# sources/storage-engines/wiredtiger/test/suite/test_txn_uncommitted.py

## Purpose
`test_txn_uncommitted.py` validates connection and session statistics for uncommitted transaction updates and dirty bytes.

## Important APIs, Types, and Functions
The class defines `get_sstat`, `get_cstat`, `txn_one`, `txn_two`, `txn_two_seq`, `txn_many`, `txn_many_many`, and `test_session_stats`. It uses `wiredtiger.stat.conn.cache_updates_txn_uncommitted_count`, `cache_updates_txn_uncommitted_bytes`, `stat.session.txn_updates`, and `txn_bytes_dirty`.

## Control Flow
The test creates a table, then runs cases with one session, two concurrent sessions, two sequential sessions, many sessions with one update each, and many sessions with many updates each. After each write, commit, or rollback, it checks connection aggregate counts/bytes and per-session stats.

## State and Persistence Behavior
The durable table data is secondary. The important state is live uncommitted update accounting, which must increase as updates are made and return to zero after commit or rollback.

## Dependencies and Integration Points
Depends on all-statistics connection config, statistics cursors, and many active sessions.

## Risks and Edge Cases
Byte assertions use greater-than or greater-equal because internal overhead exceeds value length and can vary.

## Test Signals
Connection counts/bytes and session update/dirty-byte stats match expected values at each step and reset after transactions resolve.
