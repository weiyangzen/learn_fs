<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat09.py -->
# sources/storage-engines/wiredtiger/test/suite/test_stat09.py

Purpose: verifies connection statistics for the oldest active read timestamp and the timestamp range pinned by that reader.

Important APIs/types/functions: `test_stat09` uses timestamped transactions, random insert order, `statistics:`, helper `check_stats`, and helper `check_stat_oldest_read`. It inspects stats by description string rather than `wiredtiger.stat` constants.

Control flow: create a table, insert keys 1 through 100 with commit timestamp equal to key, open a reusable stats cursor, confirm no active reader reports zero, then create five sessions with read timestamps 10, 20, 30, 40, and 50. Commit readers and advance oldest timestamp through several values, checking oldest-reader and pinned-range stats after each change. Commit the remaining readers and verify stats return to zero.

State and persistence behavior: state is transactional: active sessions pin read timestamps independently of newest commits and oldest timestamp. Pinned range is computed relative to oldest timestamp only when oldest is at or beyond the active reader.

Dependencies/integration points: covers timestamp manager, active transactions, connection stats, session lifetimes, and randomized writes. Risks include stat description text coupling; signals are exact stat values at every phase.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat09.py -->
